class InsightService:
    def generate_insights(self, transcript_text: str):
        pass

class MockInsightService(InsightService):
    def generate_insights(self, transcript_text: str):
        return {
            "overview": "This is a mocked insight overview.",
            "competencies": ["Backend Architecture", "Data Engineering"],
            "technologies": ["PostgreSQL", "FastAPI"],
            "architecture": ["Microservices", "Event-Driven"],
            "resume_bullet": "Designed a backend architecture with PostgreSQL and FastAPI."
        }
