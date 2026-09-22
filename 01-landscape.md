# Landscape (as of mid-2026)

This section does not provide an exhaustive technical breakdown of each protocol; comprehensive external documentation already exists. Instead, the focus is narrower: evaluating what each relevant component of the M2M payment landscape provides, and identifying where it falls short of this proposal's objectives.

Four questions are used to compare them:

1. **No crypto required?** Can an end client pay without holding or signing with a cryptocurrency wallet?
2. **Fiat / MoR-native?** Does the protocol itself offload tax and compliance liability to a Merchant of Record, or does the seller remain liable?
3. **Agent-native payment flow?** Is there a native, machine-friendly challenge/response or session mechanism (something an autonomous agent can drive without human-shaped signup flows)?
4. **Granular multi-agent delegation?** Can a paid budget be split into independently verifiable, revocable sub-budgets for a swarm of sub-agents, without further round-trips to a central authority?

## L402

Lightning-native, built on [Macaroons](https://doi.org/10.14722/ndss.2014.23212) for authentication and attenuation ([L402](https://github.com/lightninglabs/L402)). This protocol represents the direct technical inspiration for using [Biscuit tokens](https://www.biscuitsec.org/) (chosen over Macaroons to avoid shared symmetric keys across verifying endpoints). While L402 demonstrates the viability of cryptographic delegation, it is bound to a settlement rail (the Lightning Network) that creates taxable disposal friction for European businesses. It provides no fiat on-ramp, no Merchant of Record abstraction, and requires client-side wallet infrastructure.

## X402

An HTTP 402-based standard ([X402](https://github.com/x402-foundation/x402)) historically centered on stablecoin settlement (primarily on Base). It introduces a `Facilitator` role for verification and settlement. While the v2 specification introduces abstraction hooks for legacy payment rails (ACH, SEPA, credit cards), production implementations without client-signed cryptographic authorizations remain unconfirmed as of mid-2026. X402 lacks native constructs for hierarchical, multi-agent budget partitioning; its wallet-based session mechanism (SIWx) provides reusable authorization, but not delegated offline sub-budgets.

## MPP (Machine Payments Protocol)

Backed by Stripe and Tempo Labs ([MPP](https://mpp.dev)), designed to be payment-method agnostic (supporting stablecoins, credit cards via Shared Payment Tokens, and deferred billing). MPP provides a verified mechanism for card-based fiat settlement without client-side crypto wallets. It defines two payment intents: one-shot `charge` and pre-funded `session` (using off-chain vouchers to avoid per-call settlement). While session support is currently confirmed only on crypto rails (Tempo), MPP does not act as a Merchant of Record (leaving indirect tax liability to the vendor) and provides no cryptographic delegation primitives for agent swarms.

## MoR-Backed Marketplaces (e.g., Google Cloud Marketplace + AP2)

Distribution platforms rather than open wire protocols. Google Cloud Marketplace acts contractually as Merchant of Record for third-party software, composing with the Agent Payments Protocol ([AP2](https://github.com/google-agentic-commerce/AP2)) for automated procurement. While this provides fiat billing with automated tax handling, entitlements are managed strictly at the buyer account boundary. It provides no mechanism for the purchaser to cryptographically attenuate that entitlement into autonomous, offline-verifiable sub-budgets for a downstream agent swarm.

## Summary

| Protocol / Platform | No Crypto Required | Fiat / MoR-Native | Agent-Native Flow | Granular Swarm Delegation |
|---|---|---|---|---|
| **[L402](https://github.com/lightninglabs/L402)** | No | No | Yes | Yes (via [Macaroons](https://doi.org/10.14722/ndss.2014.23212)) |
| **[X402](https://github.com/x402-foundation/x402)** | No (fiat unconfirmed) | No | Yes | No |
| **[MPP](https://mpp.dev)** | Yes (charge mode) | No | Yes | No |
| **MoR Marketplaces (GCM + [AP2](https://github.com/google-agentic-commerce/AP2))** | Yes | Yes | Yes | No |
| **This Proposal** | Yes | Yes | No (settled upfront) | Yes (via [Biscuits](https://www.biscuitsec.org/)) |

No existing approach satisfies all four criteria simultaneously. L402 demonstrates capability delegation, but binds settlement to a cryptocurrency network that introduces tax friction for European businesses. Conversely, existing fiat and MoR solutions govern access only at the level of a single purchasing entity, lacking mechanisms to delegate that entitlement down to an autonomous agent swarm. Bridging that operational gap constitutes the primary scope of this proposal.

*Verified with primary sources as of mid-2026. This space moves fast enough that some of the above may already be outdated by the time you're reading it. Corrections welcome via issue.*

