from __future__ import annotations

from chatbot.llm import LLMClient
from logging_utils import get_logger


class Actor:

    def __init__(self, llm: LLMClient, system_prompt: str):
        self._llm = llm
        self._system_prompt = system_prompt
        self._logger = get_logger(self.__class__.__name__)

    def answer(self, question: str, history: list[dict]) -> str:
        messages = [{"role": "system", "content": self._system_prompt}] + history + [{"role": "user", "content": question}]
        reply = self._llm.chat(messages)
        self._logger.info(
            "Actor answered",
            extra={"extra_data": {"model": self._llm.model, "question": question, "history_messages": len(history)}},
        )
        return reply
