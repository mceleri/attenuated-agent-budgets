"""
Orchestrator implementation for Attenuated Agent Budgets.
Receives the Master Token (Block 0) and attenuates sub-budgets offline
for autonomous sub-agents without contacting the Provider.
"""

from typing import Tuple, List
from biscuit_auth import Biscuit, BlockBuilder, PublicKey


class Orchestrator:
    def __init__(self, master_token_b64: str, provider_public_key: PublicKey):
        self.master_token_b64 = master_token_b64
        self.provider_public_key = provider_public_key

    def attenuate_sub_budget(
        self,
        sub_agent_id: str,
        allowed_endpoint: str,
        max_call_cents: int,
    ) -> Tuple[str, str]:
        """
        Derives an attenuated Biscuit token for a sub-agent completely offline.
        Appends a block containing:
        - Binding check to ambient::sub_agent_id
        - Whitelist check on ambient::endpoint
        - Ceiling check on ambient::request_cost

        Returns: (attenuated_token_b64, block_revocation_id)
        """
        parent_biscuit = Biscuit.from_base64(self.master_token_b64, self.provider_public_key)
        
        block_builder = BlockBuilder(f"""
            check if ambient::sub_agent_id("{sub_agent_id}");
            check if ambient::endpoint("{allowed_endpoint}");
            check if ambient::request_cost($cost), $cost <= {max_call_cents};
        """)

        attenuated_biscuit = parent_biscuit.append(block_builder)
        
        # The last revocation_id in the list corresponds to the freshly appended block
        block_revocation_id = attenuated_biscuit.revocation_ids[-1]
        
        return attenuated_biscuit.to_base64(), block_revocation_id
