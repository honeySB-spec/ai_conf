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

from fastapi.responses import StreamingResponse
import asyncio
import json
import threading

router = APIRouter()

# Initialize the Crew
event_crew = EventPlanningCrew()

@router.post("/plan")
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
        StreamingResponse: SSE stream of the event plan.

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
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def sync_callback(task_output):
            # TaskOutput has agent and raw
            if hasattr(task_output, 'raw'):
                agent_role = getattr(task_output.agent, 'role', 'Agent') if hasattr(task_output, 'agent') and task_output.agent else 'Agent'
                content = task_output.raw
            else:
                agent_role = "Agent"
                content = str(task_output)
            
            # Save message to database asynchronously
            from src.data.db_manager import db_manager
            asyncio.run_coroutine_threadsafe(
                db_manager.save_message(session.id, agent_role, content),
                loop
            )
            
            # Send structured data for better UI rendering
            chunk = {
                "agent": agent_role,
                "content": content
            }
            loop.call_soon_threadsafe(queue.put_nowait, chunk)

        def worker():
            try:
                event_crew.kickoff(context_dict, task_callback=sync_callback)
                loop.call_soon_threadsafe(queue.put_nowait, "[DONE]")
            except Exception as e:
                logger.error("worker_error", error=str(e), exc_info=True)
                loop.call_soon_threadsafe(queue.put_nowait, f"ERROR: {str(e)}")
                loop.call_soon_threadsafe(queue.put_nowait, "[DONE]")

        threading.Thread(target=worker, daemon=True).start()

        async def sse_generator():
            while True:
                chunk = await queue.get()
                if chunk == "[DONE]":
                    yield f"data: {json.dumps('[DONE]')}\n\n"
                    break
                if str(chunk).startswith("ERROR: "):
                    yield f"data: {json.dumps(chunk)}\n\n"
                    break
                yield f"data: {json.dumps(chunk)}\n\n"

        logger.info("event_plan_streaming_started", session_id=session.id)
        return StreamingResponse(sse_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.error("event_plan_request_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_sessions(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Get all event planning sessions for the current user."""
    from src.data.db_manager import db_manager
    sessions = await db_manager.get_user_sessions(session.user_id)
    return sessions


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    request: Request,
    current_session: Session = Depends(get_current_session),
):
    """Get all messages/reports for a specific session."""
    from src.data.db_manager import db_manager
    # Ensure the user owns this session or it's their current one
    messages = await db_manager.get_session_messages(session_id)
    return messages

