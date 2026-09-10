import json
import unittest
from unittest.mock import call, patch

import next_agent


class NextAgentTest(unittest.TestCase):
    def test_focus_uses_pane_ids_and_cycles_in_pane_order(self):
        agents = [
            {"pane_id": "w1:p2", "terminal_id": "term_a", "agent_status": "done"},
            {"pane_id": "w1:p1", "terminal_id": "term_z", "agent_status": "done"},
        ]

        for focused, expected in [
            (None, "w1:p1"),
            ("w1:p1", "w1:p2"),
            ("w1:p2", "w1:p1"),
        ]:
            with self.subTest(focused=focused):
                for agent in agents:
                    agent["focused"] = agent["pane_id"] == focused

                response = json.dumps({"result": {"agents": agents}})
                with (
                    patch("next_agent.load_config", return_value=next_agent.DEFAULTS),
                    patch("next_agent.run_herdr", return_value=response) as run_herdr,
                ):
                    next_agent.main()

                self.assertEqual(run_herdr.call_args_list, [
                    call("agent", "list"),
                    call("agent", "focus", expected),
                ])


if __name__ == "__main__":
    unittest.main()
