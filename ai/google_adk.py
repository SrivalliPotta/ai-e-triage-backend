import json
import os
import uuid

from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def _load_env_file(env_path: str = ".env") -> None:
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith("#"):
                continue

            if "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)

            key = key.strip()
            value = value.strip().strip('"').strip("'")

            os.environ.setdefault(key, value)


_load_env_file()


root_agent = Agent(
    model=os.getenv("GOOGLE_ADK_MODEL", "gemini-2.5-flash"),
    name="incident_summary_agent",
    description="Summarizes emergency incident operations.",
    instruction=(
        "You are an emergency triage operations assistant. "
        "Given structured incident data, produce a concise operational summary. "
        "Focus on triage severity, risk, workflow state, and required resources. "
        "Keep summaries short and actionable."
    ),
)


class GoogleADKClient:
    def __init__(self):
        self.session_service = InMemorySessionService()

        self.runner = Runner(
            agent=root_agent,
            app_name="incident_summary_app",
            session_service=self.session_service,
        )

    async def summarize_incident(
        self,
        incident_data: dict,
    ) -> str:

        try:
            prompt = self._build_prompt(incident_data)

            user_id = "incident_summary_service"
            session_id = str(uuid.uuid4())

            await self.session_service.create_session(
                app_name="incident_summary_app",
                user_id=user_id,
                session_id=session_id,
            )

            content = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt)
                ],
            )

            responses = []

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):

                if not event.content:
                    continue

                for part in event.content.parts:

                    text = getattr(part, "text", None)

                    if text:
                        responses.append(text)

            if not responses:
                return "No AI summary generated."

            return "\n".join(responses).strip()

        except Exception as exc:
            return f"Google ADK summarization failed: {str(exc)}"

    def _build_prompt(
        self,
        incident_data: dict,
    ) -> str:

        payload = json.dumps(
            incident_data,
            indent=2,
            sort_keys=True,
        )

        return f"""
Summarize this emergency incident for command-center staff.

Provide:
- triage severity
- patient condition
- operational concerns
- recommended focus

Keep it concise and actionable.

Incident Payload:
{payload}
"""