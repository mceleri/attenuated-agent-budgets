# Attenuated Agent Budgets: Biscuits-Based Sub-Budget Delegation for Multi-Agent Swarms via Merchant-of-Record-Funded Payments

The growing interest in Machine-to-Machine (M2M) microtransactions has produced several protocol standards (L402, X402, and more recently MPP) that let autonomous agents pay for services on a per-request basis, typically settled through cryptocurrency or wallet-based rails.
For freelancers and small-to-medium enterprises (SMEs) operating primarily under European tax regimes, however, this model introduces a structural obstacle rather than a convenience: current legislation in jurisdictions such as Italy and Spain treats each crypto-denominated payment as a taxable disposal event, with no de minimis exemption. Settling hundreds or thousands of micro (cents or even sub-cents) transactions autonomously is, in practice, unworkable for this target group, regardless of protocol efficiency.

**This whitepaper deliberately narrows its scope to a niche but well-defined scenario:**
single entities or providers who

- (a) cannot or will not rely on cryptocurrency
- (b) want to offload tax and compliance responsibility to a Merchant of Record (MoR)
- (c) still wish to expose pay-per-use M2M services to swarms of autonomous sub-agents.

Reconciling these constraints requires breaking with the core assumption shared by L402, X402, and MPP that each individual use can be paid for autonomously and separately.
Instead, payment can be decoupled from access delegation: a single, human-authorized transaction is processed through a MoR, and a "Master Biscuit" is issued upon successful settlement.
This biscuit acts purely as a locally verifiable, cryptographically attenuable access-control credential, independent of any specific M2M payment protocol.

A primary orchestrator agent can attenuate the Master Biscuit offline into strict sub-budgets, distributing them to autonomous sub-agents without further interaction with the orchestrator.
Of course there is an architectural cost for this approach:

- verifying endpoints must maintain server-side state to enforce cumulative spend limits across sub-agents, since caveats alone cannot guarantee a global ceiling without such tracking
- revocation must be handled explicitly in case of MoR-side disputes or refunds
- biscuit public-key must be shared across all the services that want to verify the biscuit integrity/validity.

This proposal does not claim to generalize beyond its target scenario, nor to compete with the throughput or autonomy of crypto-native M2M payment protocols.

Also, enterprise-grade platforms already combine agent-facing distribution with a genuine Merchant-of-Record model.
Google Cloud Marketplace, for instance, contractually acts as merchant of record for third-party listings, and is positioned to compose with Google's Agent Payments Protocol (AP2) for autonomous, agent-driven procurement.
Such platforms, however, govern entitlement at the level of the purchasing customer; to the best of my knowledge, as of mid-2026, none of them offers the purchasing entity a way to further attenuate that entitlement into independently verifiable, revocable sub-budgets for its own swarm of autonomous sub-agents.
This is the narrower gap addressed here: not the complete absence of MoR-backed M2M monetization, but the absence of granular, offline-attenuable delegation once such a budget has already been acquired without using a blockchain.
