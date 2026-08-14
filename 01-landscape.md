# Landscape (as of mid-2026)

This is not a deep technical breakdown of each protocol, plenty of good documentation exists for that already, and it would age faster than this whitepaper. The goal here is narrower: for each relevant piece of the M2M payment landscape, what does it actually offer, and where does it stop short of what this whitepaper proposes?

Four questions are used to compare them:

1. **No crypto required?** Can an end client pay without holding or signing with a cryptocurrency wallet?
2. **Fiat / MoR-native?** Does the protocol itself offload tax and compliance liability to a Merchant of Record, or does the seller remain liable?
3. **Agent-native payment flow?** Is there a native, machine-friendly challenge/response or session mechanism (something an autonomous agent can drive without human-shaped signup flows)?
4. **Granular multi-agent delegation?** Can a paid budget be split into independently verifiable, revocable sub-budgets for a swarm of sub-agents, without further round-trips to a central authority?

## L402

Lightning-native, built on macaroons for authentication and (in principle) attenuation. This is the direct technical inspiration for this whitepaper's use of macaroons. The cryptographic delegation model already exists here, it's just tied to a settlement rail (Lightning) this whitepaper's target audience can't use. No fiat path, no MoR concept, requires a Lightning-capable wallet on the client side.

## X402

HTTP 402-based, built around stablecoin settlement (predominantly on Base). Introduces a `Facilitator` role for payment verification/settlement, and v2 has announced compatibility with legacy fiat rails (ACH, SEPA, card networks) but as of mid-2026, no production implementation of a pure fiat, wallet-free payment flow has been confirmed; the one concrete fiat-adjacent integration found (Stripe) still requires a client-signed crypto authorization under the hood. No native mechanism for splitting a budget across sub-agents; v2 is introducing wallet-based sessions (SIWx), which is a step toward reusable authorization but not attenuated sub-delegation.

## MPP (Machine Payments Protocol)

Stripe/Tempo-backed, payment-method agnostic by design (stablecoins, cards via Shared Payment Tokens, BNPL). This is the first protocol in this landscape that genuinely supports fiat/card payment without a client-side wallet. Two payment intents exist: one-shot `charge` and pre-funded `session` (escrow + off-chain vouchers, avoiding per-call settlement) but sessions are, as of mid-2026, confirmed only on the crypto (Tempo) rail; the fiat/card path's support for the session model is unconfirmed. No native MoR: the merchant remains merchant of record by default (Stripe Managed Payments could change this, but no confirmed integration with MPP exists yet). No native sub-agent budget delegation.

## MoR-backed agent marketplaces (e.g. Google Cloud Marketplace + AP2)

Not a payment protocol in the same sense, a distribution platform. Google Cloud Marketplace contractually acts as Merchant of Record for third-party listings, and is positioned to compose with Google's Agent Payments Protocol (AP2) for agent-driven procurement. This is the closest existing match to "fiat, MoR-backed, agent-facing" but entitlement is governed at the level of the purchasing customer/account. Nothing found lets that customer further attenuate their entitlement into independent, revocable sub-budgets for their own agent swarm.

## Summary

| | No crypto required | Fiat / MoR-native | Agent-native flow | Granular sub-agent delegation |
|---|---|---|---|---|
| L402 | ❌ | ❌ | ✅ | ✅ (via macaroons) |
| X402 | ❌ (fiat path unconfirmed) | ❌ | ✅ | ❌ |
| MPP | ✅ (charge only, confirmed) | ❌ (MoR unconfirmed) | ✅ | ❌ |
| MoR marketplaces (GCM + AP2) | ✅ | ✅ | ✅ | ❌ |
| **This whitepaper** | ✅ | ✅ | ❌ (Payment happens once, upfront) | ✅ |

No existing option checks every column at once. L402 has the delegation mechanism this whitepaper borrows from, but on the wrong settlement rail for the target audience. Everything fiat/MoR-capable stops at the level of a single purchasing entity, without a way to further delegate that budget down into an agent swarm. That gap is the whitepaper's actual scope, not a claim that M2M payments or MoR-backed monetization don't exist yet, both clearly do.

*Verified with primary sources as of mid-2026. This space moves fast enough that some of the above may already be outdated by the time you're reading it. Corrections welcome via issue.*

