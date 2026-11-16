from __future__ import annotations

from chatbot.context import build_critic_user_prompt
from chatbot.llm import LLMClient
from chatbot.models import Evaluation
from logging_utils import get_logger


class Critic:

    def __init__(self, llm: LLMClient, system_prompt: str):
        self._llm = llm
        self._system_prompt = system_prompt
        self._logger = get_logger(self.__class__.__name__)

    @property
    def model(self) -> str:
        return self._llm.model

    def evaluate(self, question: str, answer: str, history: list[dict]) -> Evaluation:
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": build_critic_user_prompt(question, answer, history)},
        ]
        evaluation = self._llm.parse(messages, Evaluation)
        self._logger.info(
            "Critic evaluated answer",
            extra={"extra_data": {
                "model": self._llm.model,
                "question": question,
                "is_acceptable": evaluation.is_acceptable,
                "feedback": evaluation.feedback,
            }},
        )
        return evaluation
