from __future__ import annotations

from chatbot.context import build_revision_section
from chatbot.llm import LLMClient
from logging_utils import get_logger


class Actor:

    def __init__(self, llm: LLMClient, system_prompt: str):
        self._llm = llm
        self._system_prompt = system_prompt
        self._logger = get_logger(self.__class__.__name__)

    def answer(
        self,
        question: str,
        history: list[dict],
        rejected_answer: str | None = None,
        feedback: str | None = None,
    ) -> str:
        system_prompt = self._system_prompt
        if rejected_answer is not None:
            system_prompt += build_revision_section(rejected_answer, feedback or "")

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": question}]
        reply = self._llm.chat(messages)
        self._logger.info(
            "Actor answered",
            extra={"extra_data": {
                "model": self._llm.model,
                "question": question,
                "history_messages": len(history),
                "is_revision": rejected_answer is not None,
            }},
        )
        return reply
