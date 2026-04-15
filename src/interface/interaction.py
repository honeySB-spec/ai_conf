"""Conference Organizer API endpoints for generating structured event plans.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from src.interface.auth import get_current_session
from src.config.settings import settings
from src.system.rate_limit import limiter
from src.system.logs import logger
from src.data.models.session import Session
from src.data.schemas.event import EventContextRequest, PlanResponse
from src.agent.crew import EventPlanningCrew

from fastapi.concurrency import run_in_threadpool

router = APIRouter()

# Initialize the Crew
event_crew = EventPlanningCrew()

@router.post("/plan", response_model=PlanResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["chat"][0])
async def generate_plan(
    request: Request,
    event_context: EventContextRequest,
    session: Session = Depends(get_current_session),
):
    """Process an event planning request using the multi-agent CrewAI.

    Args:
        request: The FastAPI request object for rate limiting.
        event_context: The structured event context.
        session: The current session from the auth token.

    Returns:
        PlanResponse: The processed and structured event plan.

    Raises:
        HTTPException: If there's an error processing the request.
    """
    try:
        logger.info(
            "event_plan_request_received",
            session_id=session.id,
            event_type=event_context.event_type
        )

        context_dict = event_context.model_dump()
        result = await run_in_threadpool(event_crew.kickoff, context_dict)

        logger.info("event_plan_generated", session_id=session.id)

        return PlanResponse(plan=result)
    except Exception as e:
        logger.error("event_plan_request_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
