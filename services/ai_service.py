from ai.google_adk import GoogleADKClient


class AIService:
    def __init__(self, adk_client: GoogleADKClient | None = None):
        self.client = adk_client or GoogleADKClient()

    def summarize_incident(self, incident_data: dict) -> str:
        return self.client.summarize_incident(incident_data)
