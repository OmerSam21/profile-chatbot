from __future__ import annotations

from collections.abc import Iterator

import gradio as gr

from chatbot.actor import Actor
from chatbot.answer_loop import AnswerLoop, Stage
from chatbot.context import build_actor_system_prompt, build_critic_system_prompt, load_profile_sources
from chatbot.critic import Critic
from chatbot.llm import create_llm_client
from chatbot.models import Outcome, QuestionRun
from const import ACTOR_MODEL, ACTOR_PROVIDER, CRITIC_MODEL, CRITIC_PROVIDER, MAX_ATTEMPTS

_TITLE = "צ׳אט פרופיל אישי"
_DESCRIPTION = "שאלו אותי על לימודים, ניסיון, מיומנויות ופרויקטים. (פרופיל לדוגמה)"
_EXAMPLES = [
    "ספר לי על הרקע המקצועי שלך",
    "איפה למדת?",
    "באילו טכנולוגיות אתה עובד?",
    "מה הפרויקט שאתה הכי גאה בו?",
]
_STAGE_MESSAGES = {
    Stage.GENERATING: "מנסח תשובה…",
    Stage.VALIDATING: "מאמת את התשובה…",
}
_EXHAUSTED_MESSAGE = f"לא הצלחתי לנסח תשובה מדויקת מספיק לשאלה הזו גם אחרי {MAX_ATTEMPTS} ניסיונות. אפשר לנסח אותה מחדש?"
_ERROR_MESSAGE = "אירעה תקלה טכנית ולא הצלחתי להשלים את התשובה. נסו שוב בעוד רגע."


def final_message(run: QuestionRun) -> str:
    if run.outcome == Outcome.APPROVED:
        return run.final_answer
    if run.outcome == Outcome.ATTEMPTS_EXHAUSTED:
        return _EXHAUSTED_MESSAGE
    return _ERROR_MESSAGE


class ChatApp:

    def __init__(self, loop: AnswerLoop):
        self._loop = loop

    def respond(self, message: str, history: list[dict], request: gr.Request | None = None) -> Iterator[str]:
        scenario_id = request.session_hash if request else "unknown"
        for step in self._loop.run(message, history, scenario_id):
            yield _STAGE_MESSAGES[step] if isinstance(step, Stage) else final_message(step)

    def build(self) -> gr.ChatInterface:
        return gr.ChatInterface(
            self.respond,
            title=_TITLE,
            description=_DESCRIPTION,
            examples=_EXAMPLES,
            chatbot=gr.Chatbot(rtl=True, show_label=False),
            textbox=gr.Textbox(rtl=True, placeholder="כתבו שאלה...", show_label=False),
        )


def build_actor_and_critic() -> tuple[Actor, Critic]:
    sources = load_profile_sources()
    actor = Actor(create_llm_client(ACTOR_PROVIDER, ACTOR_MODEL), build_actor_system_prompt(sources))
    critic = Critic(create_llm_client(CRITIC_PROVIDER, CRITIC_MODEL), build_critic_system_prompt(sources))
    return actor, critic


def main() -> None:
    ChatApp(AnswerLoop(*build_actor_and_critic())).build().launch(inbrowser=True)


if __name__ == "__main__":
    main()
