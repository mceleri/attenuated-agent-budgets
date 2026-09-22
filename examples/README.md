# Attenuated Agent Budgets - Reference Implementation

This directory provides an executable reference implementation of the attenuated Biscuit budget architecture described in the whitepaper.

## Prerequisites

- Python 3.10+
- `biscuit-python >= 0.4.0`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Demo

Execute the complete end-to-end demonstration:
```bash
python3 demo.py
```

## Architecture Mapping

| Component | File | Whitepaper Chapter Mapping |
|---|---|---|
| **API Provider** | [`provider.py`](./provider.py) | - Root KeyPair management & Block 0 minting ([`02-architecture.md`](../02-architecture.md#2-cryptographic-primitive-biscuit-tokens) Section 2)<br>- Two-phase dynamic pricing hold/capture ([`02-architecture.md`](../02-architecture.md#61-two-phase-settlement-for-dynamic-costs-hold--capture) Section 6.1)<br>- Top-up re-crediting ([`02-architecture.md`](../02-architecture.md#62-budget-top-up) Section 6.2)<br>- Surgical revocation store ([`02-architecture.md`](../02-architecture.md#72-tier-2-surgical-sub-agent-revocation) Section 7.2)<br>- HTTP status code handling ([`03-wire-protocol.md`](../03-wire-protocol.md#4-http-status-codes--error-response-matrix) Section 4) |
| **Orchestrator** | [`orchestrator.py`](./orchestrator.py) | - Offline attenuation ([`02-architecture.md`](../02-architecture.md#3-attenuation--datalog-semantics) Section 3)<br>- Extraction of block revocation IDs ([`02-architecture.md`](../02-architecture.md#72-tier-2-surgical-sub-agent-revocation) Section 7.2) |
| **End-to-End Suite** | [`demo.py`](./demo.py) | - Exercises all 7 protocol phases end-to-end |

## Demonstrated Lifecycle Phases

1. **Initial MoR Settlement:** User deposits €10.00 via Merchant of Record checkout. Provider initializes the database ledger on `checkout_id` and mints Master Token Block 0.
2. **Offline Attenuation:** Orchestrator derives two restricted sub-agent tokens completely offline (no network contact with Provider):
   - `token_search`: Restricted to `/v1/search`, max €0.50 per call.
   - `token_synth`: Restricted to `/v1/synthesize`, max €3.00 per call.
3. **Fixed-Cost Invocation:** Search agent executes a €0.20 call. Provider validates ambient checks and debits ledger (`200 OK`, €9.80 remaining).
4. **Datalog Policy Enforcement:**
   - Search agent attempts unauthorized endpoint `/v1/synthesize` $\rightarrow$ Blocked (`403 Forbidden`).
   - Search agent attempts call exceeding €0.50 ceiling $\rightarrow$ Blocked (`403 Forbidden`).
5. **Two-Phase Metering (Hold & Capture):** Synthesis agent reserves pessimistic €2.50 hold on ledger, generates 1,420 LLM tokens (actual cost €0.85), and captures €0.85, releasing €1.65 unspent remainder back to available balance.
6. **Budget Exhaustion & Seamless Top-Up:** When available balance reaches €0.00, requests fail with `402 Payment Required`. An MoR webhook adds €5.00 to the existing `checkout_id`. The agent retries using the *exact same Biscuit token* without re-issuance or re-attenuation (`200 OK`).
7. **Surgical Revocation:** Orchestrator revokes the search agent's block `revocation_id` via `POST /v1/budgets/revoke`. Subsequent calls from the search agent fail immediately (`410 Gone / Revoked`), while the synthesis agent continues operating unaffected (`200 OK`).
