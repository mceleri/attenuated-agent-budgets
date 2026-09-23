#!/usr/bin/env python3
"""
Attenuated Agent Budgets - End-to-End Reference Implementation Demo.
Demonstrates:
1. MoR Initial Settlement & Master Token Minting (Block 0).
2. Offline Attenuation by Orchestrator (No Provider contact).
3. Fixed-Cost API Invocations & ACID Ledger Debiting.
4. Cryptographic Datalog Policy Enforcement (Endpoint & Cost Ceilings).
5. Dynamic Two-Phase Metering (Hold & Capture for Generative AI).
6. Budget Exhaustion & Seamless Top-Up without Token Re-issuance.
7. Surgical Revocation of a Single Sub-Agent Block.
"""

import sys
from provider import Provider
from orchestrator import Orchestrator


def print_step(title: str):
    print("\n" + "=" * 70)
    print(f">> {title}")
    print("=" * 70)


def main():
    print("Initializing Attenuated Agent Budgets Demo...\n")

    # -------------------------------------------------------------------------
    # STEP 1: Provider Setup & MoR Fiat Settlement
    # -------------------------------------------------------------------------
    print_step("STEP 1: MoR Fiat Settlement & Master Token Issuance")
    provider = Provider()
    initial_deposit_cents = 1000  # 10.00 EUR
    user_id = "org_acme_corp"

    checkout_id, master_token_b64, revocation_secret = provider.create_checkout_and_mint(
        user_id=user_id, budget_cents=initial_deposit_cents
    )
    print(f"[*] MoR Checkout Completed: {checkout_id}")
    print(f"[*] Initial Ledger Balance: {initial_deposit_cents / 100:.2f} EUR")
    print(f"[*] Master Biscuit (Base64, snippet): {master_token_b64[:45]}...")
    print(f"[*] Admin Revocation Secret (snippet): {revocation_secret[:15]}...")

    # -------------------------------------------------------------------------
    # STEP 2: Orchestrator Offline Attenuation
    # -------------------------------------------------------------------------
    print_step("STEP 2: Orchestrator Offline Sub-Agent Attenuation")
    orchestrator = Orchestrator(master_token_b64, provider.public_key, revocation_secret)

    # Sub-Agent 1: Search Agent (Limited to /v1/search, max 0.50 EUR per call)
    agent1_id = "agent_search_01"
    token_search, rev_id_search = orchestrator.attenuate_sub_budget(
        sub_agent_id=agent1_id,
        allowed_endpoint="/v1/search",
        max_call_cents=50,
    )
    print(f"[+] Attenuated Token for {agent1_id}:")
    print(f"    - Endpoint: /v1/search")
    print(f"    - Max call cost: 0.50 EUR")
    print(f"    - Block Revocation ID: {rev_id_search[:20]}...")

    # Sub-Agent 2: Synthesis Agent (Limited to /v1/synthesize, max 3.00 EUR per call)
    agent2_id = "agent_synth_02"
    token_synth, rev_id_synth = orchestrator.attenuate_sub_budget(
        sub_agent_id=agent2_id,
        allowed_endpoint="/v1/synthesize",
        max_call_cents=300,
    )
    print(f"[+] Attenuated Token for {agent2_id}:")
    print(f"    - Endpoint: /v1/synthesize")
    print(f"    - Max call cost: 3.00 EUR")
    print(f"    - Block Revocation ID: {rev_id_synth[:20]}...")

    # -------------------------------------------------------------------------
    # STEP 3: Fixed-Cost Invocation
    # -------------------------------------------------------------------------
    print_step("STEP 3: Fixed-Cost Invocation by Sub-Agent 1")
    search_call_cost_cents = 20  # 0.20 EUR
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/search",
        cost_cents=search_call_cost_cents,
        sub_agent_id=agent1_id,
    )
    print(f"[*] Request: POST /v1/search (Cost: {search_call_cost_cents / 100:.2f} EUR)")
    print(f"[*] HTTP Status: {status}")
    print(f"[*] Response: {res}")
    assert status == 200

    # -------------------------------------------------------------------------
    # STEP 4: Datalog Policy Enforcement (Offline Checks)
    # -------------------------------------------------------------------------
    print_step("STEP 4: Datalog Policy Enforcement")
    
    # Violation 1: Search Agent tries to call unauthorized endpoint /v1/synthesize
    print("[-] Test 4A: Invoking unauthorized endpoint /v1/synthesize with search token...")
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/synthesize",
        cost_cents=50,
        sub_agent_id=agent1_id,
    )
    print(f"    HTTP Status: {status} (Expected 403)")
    print(f"    Error detail: {res.get('error')} - {res.get('message')}")
    assert status == 403

    # Violation 2: Search Agent tries to incur cost exceeding 0.50 EUR ceiling
    print("\n[-] Test 4B: Incurring 0.75 EUR cost (exceeding 0.50 EUR ceiling)...")
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/search",
        cost_cents=75,
        sub_agent_id=agent1_id,
    )
    print(f"    HTTP Status: {status} (Expected 403)")
    print(f"    Error detail: {res.get('error')} - {res.get('message')}")
    assert status == 403

    # -------------------------------------------------------------------------
    # STEP 5: Dynamic Pricing (Two-Phase Hold & Capture)
    # -------------------------------------------------------------------------
    print_step("STEP 5: Dynamic Two-Phase Metering (LLM Generation)")
    max_hold_cents = 250  # 2.50 EUR pessimistic hold
    print(f"[*] Phase 1: Requesting Hold of {max_hold_cents / 100:.2f} EUR on /v1/synthesize...")
    status, hold_res = provider.hold_two_phase(
        token_b64=token_synth,
        endpoint="/v1/synthesize",
        max_hold_cents=max_hold_cents,
        sub_agent_id=agent2_id,
    )
    print(f"    HTTP Status: {status}")
    print(f"    Hold Response: {hold_res}")
    assert status == 200
    hold_id = hold_res["hold_id"]

    # Simulating LLM Execution: 1,420 tokens generated -> Actual cost: 0.85 EUR
    actual_cost_cents = 85
    print(f"\n[*] Execution: LLM generated output. Actual cost: {actual_cost_cents / 100:.2f} EUR")
    print(f"[*] Phase 2: Capturing actual cost and releasing unspent remainder...")
    status, capture_res = provider.capture_two_phase(hold_id, actual_cost_cents)
    print(f"    HTTP Status: {status}")
    print(f"    Capture Response: {capture_res}")
    assert status == 200

    # -------------------------------------------------------------------------
    # STEP 6: Budget Exhaustion & Seamless Top-Up
    # -------------------------------------------------------------------------
    print_step("STEP 6: Budget Exhaustion & Seamless Top-Up")
    # Drain remaining balance down to 0 to simulate natural exhaustion
    curr_balance = provider.ledgers[checkout_id]["available_cents"]
    print(f"[*] Current Available Balance: {curr_balance / 100:.2f} EUR")
    print(f"[*] Simulating workload exhaustion (setting balance to 0 EUR)...")
    provider.ledgers[checkout_id]["available_cents"] = 0
    print(f"[*] Balance drained. Available: {provider.ledgers[checkout_id]['available_cents']} cents.")

    # Attempt invocation with zero balance -> 402 Payment Required
    print("\n[-] Attempting invocation with exhausted balance:")
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/search",
        cost_cents=20,
        sub_agent_id=agent1_id,
    )
    print(f"    HTTP Status: {status} (Expected 402)")
    print(f"    Response: {res}")
    assert status == 402

    # Top-Up: User pays 5.00 EUR via MoR webhook
    top_up_amount_cents = 500  # 5.00 EUR
    print(f"\n[+] Processing Top-Up webhook: Adding {top_up_amount_cents / 100:.2f} EUR to {checkout_id}...")
    top_up_res = provider.top_up_checkout(checkout_id, top_up_amount_cents)
    print(f"    Updated balance: {top_up_res['available_cents'] / 100:.2f} EUR")

    # Retry using the EXACT SAME previously issued Biscuit token
    print("\n[+] Retrying with existing token_search (No re-issuance needed):")
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/search",
        cost_cents=20,
        sub_agent_id=agent1_id,
    )
    print(f"    HTTP Status: {status}")
    print(f"    Response: {res}")
    assert status == 200

    # -------------------------------------------------------------------------
    # STEP 7: Surgical Revocation
    # -------------------------------------------------------------------------
    print_step("STEP 7: Surgical Revocation of Rogue Sub-Agent")
    print(f"[*] Orchestrator identifies compromised agent: {agent1_id}")
    print(f"[*] Target Block Revocation ID: {rev_id_search}")

    # Test 7A: Rogue or unauthorized entity attempts revocation without valid secret
    print("\n[-] Test 7A: Rogue entity attempts revocation with invalid management secret...")
    status, res = provider.revoke_block(
        checkout_id=checkout_id,
        revocation_secret="rev_sec_invalid_attacker_key",
        revocation_id=rev_id_search,
    )
    print(f"    HTTP Status: {status} (Expected 401)")
    print(f"    Response: {res}")
    assert status == 401

    # Test 7B: Orchestrator invokes revocation using authentic revocation_secret
    print("\n[+] Test 7B: Orchestrator executes revocation via management secret...")
    status, res = orchestrator.revoke_sub_agent(
        provider=provider,
        checkout_id=checkout_id,
        revocation_id=rev_id_search,
    )
    print(f"    HTTP Status: {status} (Expected 200)")
    print(f"    Response: {res}")
    assert status == 200

    # Sub-Agent 1 is now blocked
    print(f"\n[-] Attempting call with revoked {agent1_id}:")
    status, res = provider.execute_fixed_cost(
        token_b64=token_search,
        endpoint="/v1/search",
        cost_cents=20,
        sub_agent_id=agent1_id,
    )
    print(f"    HTTP Status: {status} (Expected 410)")
    print(f"    Response: {res}")
    assert status == 410

    # Sub-Agent 2 remains completely functional!
    print(f"\n[+] Verifying unaffected agent {agent2_id}:")
    status, res = provider.execute_fixed_cost(
        token_b64=token_synth,
        endpoint="/v1/synthesize",
        cost_cents=50,
        sub_agent_id=agent2_id,
    )
    print(f"    HTTP Status: {status}")
    print(f"    Response: {res}")
    assert status == 200

    print_step("DEMO COMPLETED SUCCESSFULLY: All 7 architectural phases verified.")


if __name__ == "__main__":
    main()
