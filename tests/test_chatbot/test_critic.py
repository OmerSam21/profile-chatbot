from unittest.mock import MagicMock, patch

import pytest

from chatbot.critic import Critic
from chatbot.exceptions import LLMError
from chatbot.models import Evaluation

_VERDICT = Evaluation(is_acceptable=False, feedback="Remove the Google claim.")


def _critic() -> Critic:
    llm = MagicMock()
    llm.parse.return_value = _VERDICT
    return Critic(llm, "SYSTEM")


def test_evaluate_returns_parsed_evaluation():
    assert _critic().evaluate("Where?", "Google", []) == _VERDICT


def test_evaluate_requests_evaluation_model():
    critic = _critic()
    critic.evaluate("Where?", "Google", [])
    assert critic._llm.parse.call_args.args[1] is Evaluation


@patch("chatbot.critic.build_critic_user_prompt", return_value="CASE")
def test_evaluate_sends_system_then_case(_mock_prompt):
    critic = _critic()
    critic.evaluate("Where?", "Google", [])
    assert critic._llm.parse.call_args.args[0] == [{"role": "system", "content": "SYSTEM"}, {"role": "user", "content": "CASE"}]


def test_evaluate_propagates_llm_error():
    critic = _critic()
    critic._llm.parse.side_effect = LLMError("invalid output")
    with pytest.raises(LLMError):
        critic.evaluate("Where?", "Google", [])
