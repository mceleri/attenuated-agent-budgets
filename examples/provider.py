"""
Provider implementation for Attenuated Agent Budgets (X402 mor-fiat scheme).
Simulates an API Provider with an internal ACID ledger, MoR integration,
Biscuit verification, Two-Phase Hold/Capture settlement, and surgical revocation.
"""

import time
import uuid
from typing import Dict, Any, Tuple, Optional, Set
from biscuit_auth import KeyPair, BiscuitBuilder, AuthorizerBuilder, Rule, Biscuit


class Provider:
    def __init__(self):
        # Master Ed25519 keypair for the Provider root
        self.root_keypair = KeyPair()
        self.public_key = self.root_keypair.public_key

        # ACID-like In-Memory Ledger
        # checkout_id -> { "user_id": str, "currency": str, "available_cents": int, "spent_cents": int }
        self.ledgers: Dict[str, Dict[str, Any]] = {}

        # Active Holds for dynamic two-phase pricing
        # hold_id -> { "checkout_id": str, "sub_agent_id": str, "amount_cents": int, "created_at": float }
        self.holds: Dict[str, Dict[str, Any]] = {}

        # Surgical revocation list: set of revoked block revocation IDs (hex strings)
        self.revocation_list: Set[str] = set()

    def create_checkout_and_mint(self, user_id: str, budget_cents: int) -> Tuple[str, str]:
        """
        Simulates Merchant of Record (MoR) checkout completion and mints Block 0 (Master Token).
        """
        checkout_id = f"chk_{uuid.uuid4().hex[:12]}"
        
        # Initialize ledger entry
        self.ledgers[checkout_id] = {
            "user_id": user_id,
            "currency": "EUR",
            "available_cents": budget_cents,
            "spent_cents": 0,
        }

        # Build Master Biscuit (Block 0 / Authority Block)
        datalog_block0 = f"""
            user_id("{user_id}");
            checkout_id("{checkout_id}");
            currency("EUR");
        """
        builder = BiscuitBuilder(datalog_block0)
        master_biscuit = builder.build(self.root_keypair.private_key)
        return checkout_id, master_biscuit.to_base64()

    def top_up_checkout(self, checkout_id: str, amount_cents: int) -> Dict[str, Any]:
        """
        Simulates a top-up payment via MoR re-crediting the existing checkout_id.
        No token re-issuance is required.
        """
        if checkout_id not in self.ledgers:
            raise KeyError(f"Checkout ID {checkout_id} not found.")
        
        self.ledgers[checkout_id]["available_cents"] += amount_cents
        return {
            "checkout_id": checkout_id,
            "available_cents": self.ledgers[checkout_id]["available_cents"],
            "added_cents": amount_cents,
        }

    def revoke_block(self, revocation_id: str) -> None:
        """
        Registers a block's cryptographic revocation ID into the revocation list.
        """
        self.revocation_list.add(revocation_id)

    def verify_and_authorize(
        self,
        token_b64: str,
        endpoint: str,
        cost_cents: int,
        sub_agent_id: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any], Optional[str]]:
        """
        Executes cryptographic verification, revocation checks, and Datalog evaluation.
        Returns: (http_status, details_dict, checkout_id)
        """
        try:
            biscuit = Biscuit.from_base64(token_b64, self.public_key)
        except Exception as e:
            return 401, {"error": "InvalidSignature", "message": str(e)}, None

        # Tier 2: Check surgical revocation IDs against known revocation list
        for rev_id in biscuit.revocation_ids:
            if rev_id in self.revocation_list:
                return 410, {
                    "error": "TokenRevoked",
                    "revocation_id": rev_id,
                    "message": "Block in delegation chain has been explicitly revoked."
                }, None

        # Build Authorizer and inject request ambient facts
        authorizer_builder = AuthorizerBuilder()
        datalog_ambient = f"""
            ambient::endpoint("{endpoint}");
            ambient::request_cost({cost_cents});
        """
        if sub_agent_id:
            datalog_ambient += f'ambient::sub_agent_id("{sub_agent_id}");\n'
        
        datalog_ambient += "allow if true;\n"
        authorizer_builder.add_code(datalog_ambient)

        try:
            authorizer = authorizer_builder.build(biscuit)
            authorizer.authorize()
        except Exception as e:
            return 403, {"error": "PolicyViolation", "message": str(e)}, None

        # Extract checkout_id from Block 0 facts
        query_rule = Rule(r"data($id) <- checkout_id($id)")
        results = authorizer.query(query_rule)
        if not results or not results[0].terms:
            return 403, {"error": "MalformedToken", "message": "Missing checkout_id in Block 0"}, None
        
        checkout_id = results[0].terms[0]
        return 200, {"status": "authorized"}, checkout_id

    def execute_fixed_cost(
        self,
        token_b64: str,
        endpoint: str,
        cost_cents: int,
        sub_agent_id: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Single-step invocation for fixed-cost endpoints.
        """
        status, auth_res, checkout_id = self.verify_and_authorize(
            token_b64, endpoint, cost_cents, sub_agent_id
        )
        if status != 200 or not checkout_id:
            return status, auth_res

        # Atomic Ledger Check & Settle
        ledger = self.ledgers.get(checkout_id)
        if not ledger:
            return 404, {"error": "LedgerNotFound", "checkout_id": checkout_id}

        if ledger["available_cents"] < cost_cents:
            return 402, {
                "error": "BudgetExhausted",
                "checkout_id": checkout_id,
                "available_cents": ledger["available_cents"],
                "required_cents": cost_cents,
                "topup_url": f"https://mor.example.com/checkout/{checkout_id}/topup",
            }

        ledger["available_cents"] -= cost_cents
        ledger["spent_cents"] += cost_cents

        return 200, {
            "status": "success",
            "debited_cents": cost_cents,
            "remaining_cents": ledger["available_cents"],
            "currency": ledger["currency"],
        }

    def hold_two_phase(
        self,
        token_b64: str,
        endpoint: str,
        max_hold_cents: int,
        sub_agent_id: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Phase 1 of dynamic pricing: Verifies policy and reserves max_hold_cents on ledger.
        """
        status, auth_res, checkout_id = self.verify_and_authorize(
            token_b64, endpoint, max_hold_cents, sub_agent_id
        )
        if status != 200 or not checkout_id:
            return status, auth_res

        ledger = self.ledgers.get(checkout_id)
        if not ledger:
            return 404, {"error": "LedgerNotFound", "checkout_id": checkout_id}

        if ledger["available_cents"] < max_hold_cents:
            return 402, {
                "error": "InsufficientHoldFunds",
                "checkout_id": checkout_id,
                "available_cents": ledger["available_cents"],
                "required_hold_cents": max_hold_cents,
            }

        # Atomically reserve hold
        ledger["available_cents"] -= max_hold_cents
        hold_id = f"hold_{uuid.uuid4().hex[:10]}"
        self.holds[hold_id] = {
            "checkout_id": checkout_id,
            "sub_agent_id": sub_agent_id,
            "amount_cents": max_hold_cents,
            "created_at": time.time(),
        }

        return 200, {
            "hold_id": hold_id,
            "held_cents": max_hold_cents,
            "remaining_available_cents": ledger["available_cents"],
        }

    def capture_two_phase(self, hold_id: str, actual_cost_cents: int) -> Tuple[int, Dict[str, Any]]:
        """
        Phase 2 of dynamic pricing: Settles actual execution cost and releases remainder.
        """
        if hold_id not in self.holds:
            return 404, {"error": "HoldNotFoundOrExpired", "hold_id": hold_id}

        hold = self.holds.pop(hold_id)
        checkout_id = hold["checkout_id"]
        held_cents = hold["amount_cents"]
        ledger = self.ledgers[checkout_id]

        if actual_cost_cents > held_cents:
            actual_cost_cents = held_cents  # Capped at hold ceiling

        remainder_cents = held_cents - actual_cost_cents
        ledger["available_cents"] += remainder_cents
        ledger["spent_cents"] += actual_cost_cents

        return 200, {
            "status": "captured",
            "hold_id": hold_id,
            "captured_cents": actual_cost_cents,
            "released_cents": remainder_cents,
            "current_available_cents": ledger["available_cents"],
        }
