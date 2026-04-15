from pydantic import BaseModel, Field

class EventContextRequest(BaseModel):
    event_type: str = Field(..., description="e.g., Conference, Music Festival, Sporting Event")
    event_category: str = Field(..., description="e.g., AI, Web3, EDM, Basketball")
    event_topic: str = Field(..., description="Focus or theme of the event")
    location: str = Field(..., description="City or location")
    expected_footfall: int = Field(..., description="Target number of attendees")
    max_budget: float = Field(..., description="Total maximum budget")
    target_audience: str = Field(..., description="Short description of the audience demographics")
    search_domains: str = Field(..., description="Comma separated web domains to search venues on")

class PlanResponse(BaseModel):
    plan: str = Field(..., description="The comprehensive event plan output by the Crew.")
