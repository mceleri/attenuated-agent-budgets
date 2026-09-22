# Attenuated Agent Budgets: Biscuits-Based Sub-Budget Delegation for Multi-Agent Swarms via Merchant-of-Record-Funded Payments

The growing interest in Machine-to-Machine (M2M) microtransactions has produced several protocol standards (L402 [L402], X402 [X402], and MPP [MPP]) that enable autonomous agents to pay for services per request, typically settled over cryptocurrency or wallet-based rails.
For freelancers and small-to-medium enterprises (SMEs) operating under European tax regimes, however, this model introduces structural friction: legislation in jurisdictions such as Italy and Spain treats each crypto-denominated transfer as a taxable disposal event without a de minimis exemption. Settling hundreds or thousands of micro-transactions autonomously is administrative and compliance overhead that renders per-request crypto settlement impractical for them.

This whitepaper addresses a specific operational profile: entities and providers who:
- (a) cannot or will not rely on cryptocurrency,
- (b) require tax, invoicing, and VAT compliance offloaded to a Merchant of Record (MoR), and
- (c) need to expose pay-per-use M2M services to swarms of autonomous sub-agents.

Meeting these constraints requires decoupling upfront financial settlement from programmatic access delegation. A single, human-authorized fiat transaction is processed through a MoR, issuing a "Master Biscuit" upon settlement. This token functions as a locally verifiable, cryptographically attenuable bearer credential, classified economically and legally under the EU Voucher Directive [DIRECTIVE2016_1065] as a Single-Purpose Voucher (SPV).

A primary orchestrator agent attenuates the Master Biscuit offline into bounded sub-budgets, distributing them to autonomous sub-agents without further interaction with the issuer. This approach involves deliberate architectural trade-offs:
- Verifying endpoints must maintain state to enforce cumulative spend across distributed agents, as Datalog caveats alone cannot enforce global ceilings without state tracking.
- Revocation must be supported explicitly for upstream MoR dispute/refund events and downstream agent containment.
- Provider-side verification services (and any consortium partner gateways) must configure the issuer's root public key, whereas clients and orchestrators require zero key management to attenuate and spend tokens.

Enterprise platforms (such as Google Cloud Marketplace composing with AP2 [AP2]) govern entitlement at the customer account boundary. However, as of mid-2026, existing platforms lack mechanisms for a customer to attenuate that entitlement offline into independently verifiable, revocable sub-budgets for an autonomous agent swarm. This whitepaper formalizes that delegation layer.
This is the narrower gap addressed here: not the complete absence of MoR-backed M2M monetization, but the absence of granular, offline-attenuable delegation once such a budget has already been acquired without using a blockchain.
