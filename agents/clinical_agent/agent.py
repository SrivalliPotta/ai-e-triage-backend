# agents/clinical_agent/agent.py

import os
import google.generativeai as genai

from agents.base_agent import BaseAgent
from agents.shared.context import WorkflowContext
from agents.shared.decision import AgentDecision


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


class ClinicalAgent(BaseAgent):

    async def handle(
        self,
        event: dict,
        context: WorkflowContext
    ) -> AgentDecision:

        patient = context.patient

        triage_tag = self._evaluate_triage(patient)

        risk_score = self._calculate_risk(
            triage_tag,
            patient
        )

        recommendations = []

        if risk_score >= 0.8:

            recommendations.append(
                "Immediate physician review recommended"
            )

        explanation = await self._generate_explanation(
            patient,
            triage_tag,
            risk_score
        )

        return AgentDecision(
            actions=[
                "SAVE_PATIENT",
                "UPDATE_QUEUE"
            ],
            metadata={
                "triage_tag": triage_tag,
                "risk_score": risk_score,
                "explanation": explanation
            },
            recommendations=recommendations,
            events=[
                {
                    "type": "PATIENT_TRIAGED",
                    "patient_id": patient.get("id"),
                    "triage_tag": triage_tag
                }
            ]
        )

    def _evaluate_triage(
        self,
        patient: dict
    ) -> str:

        if patient.get("can_walk"):
            return "GREEN"

        rr = patient.get("respiratory_rate", 0)

        pulse = patient.get("radial_pulse", True)

        mental = patient.get("follows_commands", True)

        breathing = patient.get("breathing", True)

        if not breathing:
            return "BLACK"

        if rr > 30:
            return "RED"

        if not pulse:
            return "RED"

        if not mental:
            return "RED"

        return "YELLOW"

    def _calculate_risk(
        self,
        triage_tag: str,
        patient: dict
    ) -> float:

        mapping = {
            "GREEN": 0.1,
            "YELLOW": 0.5,
            "RED": 0.9,
            "BLACK": 1.0
        }

        return mapping.get(triage_tag, 0.5)

    async def _generate_explanation(
        self,
        patient: dict,
        triage_tag: str,
        risk_score: float
    ) -> str:

        if not GOOGLE_API_KEY:
            return "Gemini explanation unavailable."

        prompt = f"""
        Patient Details:
        {patient}

        Triage Tag:
        {triage_tag}

        Risk Score:
        {risk_score}

        Explain briefly why this patient received this triage classification.
        """

        try:

            response = model.generate_content(prompt)

            return response.text

        except Exception as e:

            return f"Explanation generation failed: {str(e)}"