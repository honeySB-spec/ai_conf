import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from src.agent.crew import EventPlanningCrew
    print("Successfully imported EventPlanningCrew")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

try:
    print("Instantiating EventPlanningCrew...")
    crew_instance = EventPlanningCrew()
    print("Successfully instantiated EventPlanningCrew")
    
    # The kickoff method is where Crew is instantiated with the problematic embedder config
    print("Calling kickoff to trigger Crew initialization...")
    # Mock context
    context = {
        'event_type': 'tech conference',
        'event_category': 'technology',
        'location': 'San Francisco',
        'event_topic': 'AI and Agents',
        'target_audience': 'developers',
        'max_budget': 50000,
        'expected_footfall': 200,
        'search_domains': 'eventbrite.com'
    }
    
    # We only want to see if the Crew instantiation (inside kickoff) fails due to validation
    # We can probably just mock the master_event_crew.kickoff() or just let it fail later
    # but the Crew(**crew_kwargs) is what should trigger the Pydantic error.
    
    # Let's try to just run it and catch the Pydantic ValidationError
    crew_instance.kickoff(context)
    
except Exception as e:
    print(f"\nCaught Exception during Execution: {type(e).__name__}")
    print(str(e))
