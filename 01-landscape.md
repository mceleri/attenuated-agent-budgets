# Landscape (as of mid-2026)

This is not a deep technical breakdown of each protocol, plenty of good documentation exists for that already, and it would age faster than this whitepaper. The goal here is narrower: for each relevant piece of the M2M payment landscape, what does it actually offer, and where does it stop short of what this whitepaper proposes?

Four questions are used to compare them:

1. **No crypto required?** Can an end client pay without holding or signing with a cryptocurrency wallet?
2. **Fiat / MoR-native?** Does the protocol itself offload tax and compliance liability to a Merchant of Record, or does the seller remain liable?
3. **Agent-native payment flow?** Is there a native, machine-friendly challenge/response or session mechanism (something an autonomous agent can drive without human-shaped signup flows)?
4. **Granular multi-agent delegation?** Can a paid budget be split into independently verifiable, revocable sub-budgets for a swarm of sub-agents, without further round-trips to a central authority?

## L402

Lightning-native, built on Macaroons [BIRGISSON2014] for authentication and attenuation [L402]. This protocol represents the direct technical inspiration for using Biscuit tokens [COUPRIE2021] (chosen over Macaroons to avoid shared symmetric keys across verifying endpoints). While L402 demonstrates the viability of cryptographic delegation, it is bound to a settlement rail (the Lightning Network) that creates taxable disposal friction for European businesses. It provides no fiat on-ramp, no Merchant of Record abstraction, and requires client-side wallet infrastructure.

## X402

An HTTP 402-based standard [X402] historically centered on stablecoin settlement (primarily on Base). It introduces a `Facilitator` role for verification and settlement. While the v2 specification introduces abstraction hooks for legacy payment rails (ACH, SEPA, credit cards), production implementations without client-signed cryptographic authorizations remain unconfirmed as of mid-2026. X402 lacks native constructs for hierarchical, multi-agent budget partitioning; its wallet-based session mechanism (SIWx) provides reusable authorization, but not delegated offline sub-budgets.

## MPP (Machine Payments Protocol)

Backed by Stripe and Tempo Labs [MPP], designed to be payment-method agnostic (supporting stablecoins, credit cards via Shared Payment Tokens, and deferred billing). MPP provides a verified mechanism for card-based fiat settlement without client-side crypto wallets. It defines two payment intents: one-shot `charge` and pre-funded `session` (using off-chain vouchers to avoid per-call settlement). However, session support is currently confirmed only on crypto rails (Tempo). Crucially, MPP does not act as a Merchant of Record (the vendor remains liable for indirect taxation), nor does it provide cryptographic delegation primitives for agent swarms.

## MoR-Backed Marketplaces (e.g., Google Cloud Marketplace + AP2)

Distribution platforms rather than open wire protocols. Google Cloud Marketplace acts contractually as Merchant of Record for third-party software, composing with the Agent Payments Protocol (AP2 [AP2]) for automated procurement. While this provides fiat billing with automated tax handling, entitlements are managed strictly at the buyer account boundary. It provides no mechanism for the purchaser to cryptographically attenuate that entitlement into autonomous, offline-verifiable sub-budgets for a downstream agent swarm.

## Summary

| Protocol / Platform | No Crypto Required | Fiat / MoR-Native | Agent-Native Flow | Granular Swarm Delegation |
|---|---|---|---|---|
| **L402** [L402] | ❌ | ❌ | ✅ | ✅ (via Macaroons [BIRGISSON2014]) |
| **X402** [X402] | ❌ (fiat unconfirmed) | ❌ | ✅ | ❌ |
| **MPP** [MPP] | ✅ (charge mode) | ❌ | ✅ | ❌ |
| **MoR Marketplaces (GCM + AP2)** [AP2] | ✅ | ✅ | ✅ | ❌ |
| **This Proposal** | ✅ | ✅ | ❌ (Settled once upfront) | ✅ (via Biscuits [COUPRIE2021]) |

No existing option checks every column at once. L402 has the delegation mechanism this whitepaper borrows from, but on the wrong settlement rail for the target audience. Everything fiat/MoR-capable stops at the level of a single purchasing entity, without a way to further delegate that budget down into an agent swarm. That gap is the whitepaper's actual scope, not a claim that M2M payments or MoR-backed monetization don't exist yet, both clearly do.

*Verified with primary sources as of mid-2026. This space moves fast enough that some of the above may already be outdated by the time you're reading it. Corrections welcome via issue.*

