from __future__ import annotations

import gradio as gr

from chatbot.actor import Actor
from chatbot.context import build_actor_system_prompt, load_profile_sources
from chatbot.exceptions import LLMError
from chatbot.llm import create_llm_client
from const import ACTOR_MODEL, ACTOR_PROVIDER
from logging_utils import get_logger

logger = get_logger(__name__)

_TITLE = "צ׳אט פרופיל אישי"
_DESCRIPTION = "שאלו אותי על לימודים, ניסיון, מיומנויות ופרויקטים. (פרופיל לדוגמה)"
_EXAMPLES = [
    "ספר/י לי על הרקע המקצועי שלך",
    "איפה למדת?",
    "באילו טכנולוגיות את/ה עובד/ת?",
    "מה הפרויקט שאת/ה הכי גאה בו?",
]
_ERROR_MESSAGE = "אירעה שגיאה טכנית ביצירת התשובה. נסו שוב בעוד רגע."


class ChatApp:

    def __init__(self, actor: Actor):
        self._actor = actor

    def respond(self, message: str, history: list[dict]) -> str:
        try:
            return self._actor.answer(message, history)
        except LLMError as e:
            logger.error("Answer generation failed", extra={"extra_data": {"question": message, "error": str(e)}})
            raise gr.Error(_ERROR_MESSAGE) from e

    def build(self) -> gr.ChatInterface:
        return gr.ChatInterface(
            self.respond,
            title=_TITLE,
            description=_DESCRIPTION,
            examples=_EXAMPLES,
            chatbot=gr.Chatbot(rtl=True, show_label=False),
            textbox=gr.Textbox(rtl=True, placeholder="כתבו שאלה...", show_label=False),
        )


def main() -> None:
    llm = create_llm_client(ACTOR_PROVIDER, ACTOR_MODEL)
    actor = Actor(llm, build_actor_system_prompt(load_profile_sources()))
    ChatApp(actor).build().launch(inbrowser=True)


if __name__ == "__main__":
    main()
