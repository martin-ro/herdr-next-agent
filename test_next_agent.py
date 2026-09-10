import json
import unittest
from unittest.mock import call, patch

import next_agent


class NextAgentTest(unittest.TestCase):
    def test_focus_selects_the_agent_and_updates_the_client_tab(self):
        agents = [
            {"pane_id": "w1:p2", "tab_id": "w1:t2", "terminal_id": "term_a", "agent_status": "done"},
            {"pane_id": "w1:p1", "tab_id": "w1:t1", "terminal_id": "term_z", "agent_status": "done"},
        ]

        for focused, expected_pane, expected_tab in [
            (None, "w1:p1", "w1:t1"),
            ("w1:p1", "w1:p2", "w1:t2"),
            ("w1:p2", "w1:p1", "w1:t1"),
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
                    call("agent", "focus", expected_pane),
                    call("tab", "focus", expected_tab),
                ])


if __name__ == "__main__":
    unittest.main()
