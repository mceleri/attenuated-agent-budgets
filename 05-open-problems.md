# Open Problems and Architectural Trade-offs

This section documents the technical limitations, concurrency bottlenecks, security trade-offs, and open research questions inherent to the attenuated Biscuit budget architecture.

## 1. Concurrency Bottlenecks and Ledger Contention

### 1.1 The Single-Row Serialization Bottleneck
While Biscuit signature verification and Datalog policy checks execute statelessly in memory ($O(1)$ cryptographic operations), cumulative budget deduction requires a stateful write to a persistent ledger. In a relational database, concurrent transactions debiting against the same `checkout_id` must acquire a row-level exclusive lock:

```sql
SELECT available_balance FROM checkouts WHERE checkout_id = $1 FOR UPDATE;
```

When an orchestrator dispatches hundreds of sub-agents concurrently, this row becomes a serialization point. Transaction latency increases linearly with swarm concurrency, leading to database lock contention, increased connection pool wait times, and potential deadlock or lock timeout errors.

### 1.2 Mitigation Strategies and Trade-offs
Several architectures mitigate this contention, each introducing distinct trade-offs:

1. **Optimistic Concurrency Control (OCC):**
   Transactions read the version counter of the checkout record and attempt an atomic conditional update (`UPDATE checkouts SET balance = balance - :cost, version = version + 1 WHERE checkout_id = :id AND version = :version`). Under high write contention, retry amplification degrades throughput significantly.
2. **Pre-allocated Sub-pools (Partitioned Balances):**
   The orchestrator partitions the parent budget into isolated sub-allocations on the server (`checkout_id_sub1`, `checkout_id_sub2`), allowing concurrent writes against distinct database rows. However, this re-introduces the liquidity fragmentation problem that dynamic delegation seeks to eliminate.
3. **In-Memory Ledger with Asynchronous Persistence:**
   Atomic counters managed in an in-memory datastore (e.g., Redis using Lua scripts or Redis transactions) decouple real-time authorization from durable disk writes. While this yields sub-millisecond debit latencies ($>50,000\text{ ops/sec}$), catastrophic server failure before write-back to durable storage can cause balance drift.

## 2. Stateless Cryptographic Verification versus Stateful Budget Tracking

Biscuit tokens are fundamentally designed for distributed, decentralized authorization where verifying endpoints evaluate claims statelessly without querying a central authority. Conversely, economic budget enforcement is inherently stateful.

A purely stateless, in-memory evaluation can verify:
- Whether the token signature is valid under $PK_{root}$.
- Whether the ambient endpoint matches the whitelist.
- Whether the per-request cost does not exceed the ceiling ($\text{cost} \le c_{\max}$).
- Whether the request timestamp falls within $[t_{\text{start}}, t_{\text{expiry}}]$.

However, stateless cryptographic checks cannot determine:
- Whether the cumulative spending across all distributed sub-agents has exceeded the initial fiat allocation.
- Whether an individual token block was revoked out-of-band following an orchestrator request or an upstream MoR dispute notification.

Enforcing cumulative sub-budgets and revocations therefore reintroduces a dependency on a centralized datastore (such as a local PostgreSQL instance or Redis key). For the target demographic of freelancers and SMEs operating within a centralized or single-region environment, this state dependency is operationally modest: revocation checks and balance debits execute concurrently within a single local transaction or in-memory key lookup. However, it precludes deploying purely autonomous edge verification without an origin database round-trip.

## 3. Two-Phase Dynamic Metering and Orphaned Holds

### 3.1 Failure Modes in Dynamic Pricing
Generative AI and streaming execution require a two-phase protocol: reserving a pessimistic upper bound (`max_hold_amount`) before processing begins, followed by settling the actual metered cost upon completion. This introduces specific distributed system failure modes:

1. **Worker Crashes During Execution:**
   If the compute worker crashes mid-stream or the client drops the HTTP connection after 80% of tokens are generated, the active hold remains uncommitted.
2. **Network Partitions on Settle:**
   If the internal capture request between the API gateway and the billing ledger times out, the system cannot verify whether the compute was delivered or whether the hold should be released.

### 3.2 Lease-Based Hold Management
To prevent permanent liquidity locking from orphaned holds, holds must operate under a time-to-live (TTL) lease:

$$t_{\text{lease}} = \min(t_{\text{request}} + \text{TTL}_{\max}, t_{\text{expiry}})$$

- If no capture or renewal is received prior to lease expiration, an automated background reaper releases the held funds back to `available_balance`.
- **Race Condition:** If a slow worker completes execution and attempts to capture a hold *after* the reaper has expired it and the orchestrator has reallocated the balance to another sub-agent, the capture fails, forcing the provider to absorb unbilled compute costs.

## 4. Merchant of Record Chargeback Exposure vs. Irreversible Compute

### 4.1 Temporal Asymmetry of Settlement
The integration of traditional payment rails (credit cards, SEPA direct debit) with autonomous API consumption creates an asymmetric risk profile:

| Dimension | MoR Fiat Settlement | Compute Consumption |
|---|---|---|
| **Finality** | Reversible (60–180 day dispute window) | Irreversible (milliseconds) |
| **Dispute Mechanism** | Issuer chargeback (friendly fraud, stolen card) | None |
| **Marginal Cost** | Payment processing fees (~1.5% - 3% + fixed fee) | Electricity, GPU compute, hardware amortization |

When a bad actor uses a stolen payment credential to purchase a €500 budget and distributes hundreds of sub-agents to exhaust the compute within minutes, the provider faces a total loss when the cardholder initiates a chargeback weeks later. The provider forfeits both the fiat payout and the unrecoverable compute expenditure.

### 4.2 Mitigation Strategies
Providers deploying this architecture must implement operational risk controls:
- **Velocity Limits:** Restrict the maximum burn rate (€/minute) for newly registered accounts or untrusted IP ranges.
- **Progressive Escrow Release:** Withhold large budget authorizations until payment processing reaches higher settlement certainty tiers (e.g., SEPA clearing completion or 3-D Secure authentication).
- **Fraud Scoring Integration:** Tie initial token issuance to real-time risk scores provided by the MoR (e.g., Stripe Radar score) before minting Master Tokens.

## 5. Scalability Limits of Vertical Consortium Attenuation

### 5.1 Absence of Cross-Provider Rebalancing
As formalized in [Section 6.3 of the Architecture specification](./02-architecture.md#63-architectural-scope-sme-model--vertical-partitioning), multi-provider consortia avoid distributed transactions by employing vertical partitioning: the orchestrator attenuates sub-tokens with rigid endpoint constraints and disjoint sub-budgets.

While this eliminates cross-provider consensus protocols (e.g., Two-Phase Commit or Raft-based ledgers), it introduces operational rigidity:
- If Provider 2 exhausts its €2.00 allocation while Provider 1 retains €8.00 unspent, Provider 2 cannot unilaterally rebalance or draw from Provider 1's excess.
- Dynamic rebalancing requires either:
  1. An explicit out-of-band API call from the client to Provider 1 to issue a new attenuated token for Provider 2.
  2. A bilateral clearing protocol between Provider 1 and Provider 2, which re-introduces distributed ledger complexity and counterparty credit risk.

## 6. Cryptographic Proof of Possession in Constrained Agent Runtimes

### 6.1 Runtime Constraints
Binding Biscuit tokens to client keypairs via Proof of Possession (PoP / DPoP) mitigates bearer token theft. However, autonomous sub-agents frequently execute within constrained environments:
- Sandboxed WebAssembly (WASM) micro-runtimes.
- Restricted Model Context Protocol (MCP) tool execution processes.
- Ephemeral serverless containers.

In these environments, generating, storing, and accessing private keys securely (e.g., avoiding exposure in memory dumps or tool execution logs) presents operational complexity:
1. **Key Extraction Risk:** If an LLM agent has arbitrary tool-execution capabilities, a prompt injection attack could instruct the agent to inspect its local filesystem or environment variables and exfiltrate the private key.
2. **Computational Overhead:** Generating Ed25519 or ECDSA signatures for every high-frequency micro-invocation introduces non-trivial CPU overhead in high-throughput data processing pipelines compared to standard bearer token transmission over mTLS.

## 7. Authorization Asymmetry and Denial of Service in Revocation APIs

### 7.1 The Destructive Asymmetry of Bearer Revocation
In capability-based authorization, bearer credentials conflate possession with authority. While this is acceptable for metered API consumption (where the maximum exposure of token theft is bounded by the unspent credit ceiling), treating revocation as an unprivileged or bearer-accessible operation introduces severe asymmetric failure modes:

1. **Rogue Sub-Agent Fleet DoS:**
   Every attenuated Biscuit deterministically contains the serialized payloads and signatures of all ancestor blocks, including Block 0 (the Authority Block). Consequently, every sub-agent inherently possesses the cryptographic `revocation_id` of Block 0. If revocation endpoints accepted standard bearer tokens or lacked capability checks, a compromised sub-agent (e.g., via prompt injection or sandbox escape) could invoke the revocation API against Block 0's `revocation_id`, permanently disabling the entire token lineage and halting healthy sibling agents.

2. **Cross-Tenant Insecure Direct Object References (IDOR):**
   Because a block's `revocation_id` is an intrinsic SHA-256 digest of its cryptographic content rather than a secret, any party that inspects network traffic or shares verifying endpoints could observe foreign revocation IDs. If a provider's revocation registry operates as a flat, global blacklist without verifying cryptographic lineage, an attacker with a valid account could submit a competitor's observed `revocation_id`, causing an immediate Denial of Service against third-party workloads.

### 7.2 Separation of Spending from Management Authority
To mitigate these risks, the architecture enforces a strict privilege separation:
- **Operational Spending Credentials (Bearer Biscuit):** Delegated down into the agent swarm, attenuated offline, and sealed. Workers hold zero administrative authority and cannot reach management endpoints.
- **Administrative Management Credentials (`revocation_secret`):** Generated exclusively at checkout by the Provider and returned directly to the human principal or primary Orchestrator. The Orchestrator retains this secret securely and never exposes it to sub-agent worker environments.

Revocation requests must authenticate via this out-of-band management secret (or via asymmetric Proof of Possession tied to the Orchestrator's root keypair). While this resolves cross-tenant IDOR and rogue worker self-destruction, it introduces a statefulness trade-off: orchestrators must maintain durable, secure state for management secrets across process lifecycles, rather than operating in a completely stateless, ephemeral manner.

## 8. Residual Credit Reclamation and Master Token Re-issuance

### 8.1 Capital Lockup Post-Revocation
Because cryptographic revocation in Biscuit operates via immutable blacklists of block hashes, a revoked token lineage cannot be reinstated. If an orchestrator revokes an entire Master Token (for instance, following a suspected security breach of the orchestrator host) or terminates an intermediate branch with substantial unspent funds, the remaining fiat balance remains recorded in the provider's stateful ledger under `checkout_id`.

Without an explicit re-issuance mechanism, this leads to stranded capital: the customer has purchased a valid legal voucher with remaining credit, but lacking an unrevoked cryptographic credential, downstream agents cannot consume it.

### 8.2 Scope Exclusion: UX and Identity Dependencies
To prevent capital loss, production implementations should track residual balances and provide an administrative path to mint fresh Master Tokens against the remaining ledger balance.

This operational lifecycle is deliberately omitted from this whitepaper specification because its concrete design depends on the provider's customer experience architecture and identity model:
- **Authenticated Account Portals:** Providers maintaining persistent customer accounts (e.g., developer dashboards with OAuth2/OIDC logins) can readily expose a self-service management interface or administrative API to inspect residual balances and trigger token re-minting.
- **Account-less Guest Flows:** Providers offering purely ephemeral, account-less checkout experiences lack persistent principal identities. Reclaiming stranded credit in such architectures requires alternative recovery mechanisms, such as challenge-response proofs tied to payment receipts, email magic links, or utilizing the out-of-band `revocation_secret` as a recovery credential.

Because these choices are governed by commercial product requirements and UX preferences rather than core M2M cryptographic delegation primitives, balance re-minting workflows remain an open implementation decision for individual providers.


