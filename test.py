from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import json
import os
# Tool 1: A free search tool to find historical data
# Initialize the LangChain tool
search_tool = DuckDuckGoSearchRun()


# The Master Event Profile
event_context = {
    'event_type': 'Music Festival',        # e.g., Conference, Music Festival, Sporting Event
    'event_category': 'Electronic Dance Music (EDM)', # e.g., AI, Web3, EDM, Basketball
    'event_topic': 'Future of Sound',
    'location': 'Singapore',
    'expected_footfall': 15000,
    'max_budget': 500000,
    'target_audience': '18-35 Gen Z Music Fans',
    'search_domains': 'Cvent.com, eventlocations.com, peerspace.com, tagvenue.com, venuerific.com'
}


# Define a CrewAI-compatible wrapper
@tool("duckduckgo_search")
def web_search(search_query: str):
    """Search the web for information about past events and ticket prices."""
    return search_tool.run(search_query)

from crewai import LLM

llm = LLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct",
    api_key=os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")
)


@tool("Sponsor Relevance Scoring Engine")
def score_sponsors(sponsors_data: str, event_category: str, event_location: str) -> str:
    """
    Takes a JSON string of potential sponsors and scores them from 0-100 based on 
    industry relevance, geographic alignment, and historical sponsorship frequency.
    """
    try:
        # The agent will pass data as a string, so we parse it
        sponsors = json.loads(sponsors_data)
        scored_sponsors = []

        for sponsor in sponsors:
            score = 0
            # 1. Industry Relevance (Max 40 pts)
            if event_category.lower() in sponsor.get('industry', '').lower():
                score += 40
            
            # 2. Geography (Max 30 pts)
            if event_location.lower() in sponsor.get('past_locations', []):
                score += 30
                
            # 3. Historical Frequency (Max 30 pts)
            freq = sponsor.get('past_sponsorships_count', 0)
            if freq > 5:
                score += 30
            elif freq > 2:
                score += 15
                
            sponsor['relevance_score'] = score
            scored_sponsors.append(sponsor)
            
        # Sort by highest score first
        scored_sponsors = sorted(scored_sponsors, key=lambda x: x['relevance_score'], reverse=True)
        return json.dumps(scored_sponsors, indent=2)
        
    except Exception as e:
        return f"Error scoring sponsors. Ensure input is valid JSON. Error: {str(e)}"

print("Sponsor tools loaded successfully!")

from crewai import Agent, Task, Crew

# 1. Define the Agent
sponsor_agent = Agent(
    role='VP of Corporate Partnerships',
    goal='Identify, score, and draft proposals for potential event sponsors.',
    backstory="""You are an expert in B2B event marketing. You know that finding the right 
    sponsor is about data, not guessing. You look for companies that have recently sponsored 
    similar events, score them based on fit, and write highly persuasive outreach proposals.""",
    verbose=True,
    allow_delegation=False,
    # We reuse the web_search tool from the previous steps, plus our new scoring tool
    tools=[web_search, score_sponsors],
    llm=llm
)

# 2. Define the Task
# 2. Define the Task (UPDATED)
sponsor_task = Task(
    description="""
    We are organizing a {event_type} ({event_category}) in {location} focusing on "{event_topic}" targeting {target_audience}.
    
    Step 1: Use the web search tool to find 4 brands that have recently sponsored similar {event_type}s in the {event_category} space targeting {target_audience} in or near {location}.
    Step 2: Format those 4 companies into a strict JSON array string with the exact keys: "name", "industry", "past_locations", and "past_sponsorships_count".
    Step 3: ACTION REQUIRED: You MUST use the 'Sponsor Relevance Scoring Engine' tool. Pass the JSON string from Step 2 directly into this tool to rank them. Do not skip this step.
    Step 4: Review the output of the scoring tool. Take the #1 highest-scoring sponsor and write a 3-paragraph, customized sponsorship proposal targeted at their marketing team.
    
    CRITICAL INSTRUCTION: Do not output "Action: None" and stop. You must complete all 4 steps and output the final drafted proposal.
    """,
    expected_output="""
    A structured report containing:
    1. Sponsor Pipeline: A ranked list of the 4 sponsors with their relevance scores.
    2. Drafted Proposal: A professional, customized email proposal for the top-ranked sponsor.
    """,
    agent=sponsor_agent
)
print("Sponsor Agent and Task defined successfully!")







#Speaker tool
from crewai.tools import tool
import json

@tool("Speaker Influence & Relevance Scorer")
def score_speakers(speakers_data: str, event_topic: str) -> str:
    """
    Takes a JSON string of potential speakers and scores them from 0-100 based on 
    relevance to the topic, past speaking experience, and estimated influence.
    """
    try:
        speakers = json.loads(speakers_data)
        scored_speakers = []

        for speaker in speakers:
            score = 0
            
            # 1. Topic Relevance (Max 40 pts)
            if event_topic.lower() in speaker.get('expertise', '').lower():
                score += 40
            else:
                score += 20 # Partial credit if they are somewhat related
            
            # 2. Past Speaking Experience (Max 30 pts)
            if speaker.get('has_given_keynotes', False):
                score += 30
            elif speaker.get('past_events_count', 0) > 0:
                score += 15
                
            # 3. Influence / Publications (Max 30 pts)
            if speaker.get('has_publications_or_book', False):
                score += 30
            elif speaker.get('estimated_followers', 0) > 10000:
                score += 20
            elif speaker.get('estimated_followers', 0) > 5000:
                score += 10
                
            speaker['influence_score'] = score
            scored_speakers.append(speaker)
            
        # Sort by highest score first
        scored_speakers = sorted(scored_speakers, key=lambda x: x['influence_score'], reverse=True)
        return json.dumps(scored_speakers, indent=2)
        
    except Exception as e:
        return f"Error scoring speakers. Ensure input is valid JSON. Error: {str(e)}"

print("Speaker tools loaded successfully!")

import requests
import os
from crewai.tools import tool
import json

# Replace with your RapidAPI key
os.environ["RAPIDAPI_KEY"] = "1e538f0d54msh8be9c8bd60615c3p1801a4jsnf5ed6c34dd6a"

@tool("LinkedIn Profile Fetcher")
def fetch_linkedin_data(linkedin_url: str) -> str:
    """
    Fetches real-time structured profile data (experience, followers, headline) 
    from a LinkedIn URL using a RapidAPI wrapper. ONLY pass valid linkedin.com/in/ URLs.
    """
    # Note: This endpoint URL will change depending on which specific RapidAPI tool you choose.
    # This is a standard example using a common endpoint structure.
    api_endpoint = "https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead"
    
    headers = {
        "x-rapidapi-key": os.environ.get("RAPIDAPI_KEY"),
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }
    
    querystring = {"linkedin_url": linkedin_url}
    
    try:
        response = requests.get(api_endpoint, headers=headers, params=querystring)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter the JSON response to just what the Speaker Agent needs
            # You may need to adjust these exact JSON keys based on your specific RapidAPI provider
            relevant_data = {
                "name": data.get("full_name"),
                "headline": data.get("headline"),
                "follower_count": data.get("follower_count", 0),
                "recent_roles": [exp.get("title") for exp in data.get("experiences", [])[:3]],
            }
            return json.dumps(relevant_data, indent=2)
        else:
            return f"Failed to fetch profile. Status code: {response.status_code}"
    except Exception as e:
        return f"API Error: {str(e)}"

print("RapidAPI LinkedIn Tool loaded successfully! RIP Proxycurl.")

# 1. Update the Agent to include the new tool
speaker_agent = Agent(
    role='Head of Content & Speaker Relations',
    goal='Discover top-tier subject matter experts using real-time LinkedIn data and map them to agenda topics.',
    backstory="""You are a visionary event producer. You don't guess a speaker's influence; 
    you pull their actual real-time LinkedIn data to see their exact follower count and experience 
    before making a decision.""",
    verbose=True,
    allow_delegation=False,
    llm = llm,
    # Now it has 3 tools: Search, LinkedIn Fetcher, and our original Scoring Engine!
    tools=[web_search, fetch_linkedin_data, score_speakers] 
)

# 2. Update the Task with strict, multi-tool instructions
speaker_task = Task(
    description="""
    We are organizing a {event_type} ({event_category}) focusing on "{event_topic}".
    
    Step 1: Use the 'web_search' tool to find the names and exact LinkedIn Profile URLs of 3 notable thought leaders, artists, or figures relevant to "{event_topic}" or {event_category}. (Look for URLs starting with https://www.linkedin.com/in/).
    Step 2: ACTION REQUIRED: For EACH of the 3 LinkedIn URLs you found, use the 'LinkedIn Profile Fetcher' tool to extract their real-world data.
    Step 3: Take the real data you just fetched and format it into a strict JSON array string matching the keys required by your 'Speaker Influence & Relevance Scorer' tool (name, expertise, has_given_keynotes, past_events_count, has_publications_or_book, estimated_followers).
    Step 4: Pass that JSON string into the 'Speaker Influence & Relevance Scorer' tool to rank them.
    Step 5: Generate 3 cutting-edge agenda topics or performance slots for the event, assigning the highest-ranked speakers/artists to the most prominent slots.
    
    CRITICAL INSTRUCTION: You must complete all 5 steps. Do not stop until the final Agenda Mapping is produced.
    """,
    expected_output="""
    A structured report containing:
    1. Verified Roster: A ranked list of the 3 figures with their ACTUAL follower counts and influence scores.
    2. Proposed Agenda Mapping: 3 specific session/performance titles with the recommended figure assigned.
    """,
    agent=speaker_agent
)

print("Pro Speaker Agent and Task upgraded successfully!")




from crewai.tools import tool
import json

@tool("Dynamic Clustering Engine")
def dynamic_cluster(data_json: str, target_categories: str) -> str:
    """
    Takes a JSON string of companies and dynamically clusters them into the provided comma-separated target_categories.
    Example categories for Tech: "Enterprise, Startup, Tools"
    Example categories for Music: "Food & Bev, Merch, Art Installations"
    """
    try:
        companies = json.loads(data_json)
        categories = [cat.strip() for cat in target_categories.split(',')]
        
        clustered_results = {cat: [] for cat in categories}
        clustered_results["Other"] = []

        for company in companies:
            desc = company.get('description', '').lower()
            name = company.get('name', '').lower()
            
            assigned = False
            for cat in categories:
                # Simple keyword matching: check if category word is in description
                parts = cat.lower().replace('&', ' ').split()
                if any(p in desc for p in parts if len(p) > 2) or any(p in name for p in parts if len(p) > 2):
                    company['category'] = cat
                    clustered_results[cat].append(company)
                    assigned = True
                    break
            
            if not assigned:
                if len(categories) > 0:
                    company['category'] = categories[0]
                    clustered_results[categories[0]].append(company)
                else:
                    company['category'] = "Other"
                    clustered_results["Other"].append(company)

        return json.dumps(clustered_results, indent=2)
        
    except Exception as e:
        return f"Error clustering exhibitors. Ensure input is valid JSON. Error: {str(e)}"

print("Dynamic Clustering Tool loaded successfully!")


# 1. Define the Agent
exhibitor_agent = Agent(
    role='Director of Exhibition Sales',
    goal='Identify past exhibitors/vendors from similar events and cluster them into actionable sales categories.',
    backstory="""You are a tactical sales director. You know that selling booth or tent space requires targeting the right mix of vendors tailored to the specific event type. You systematically scrape competitor events to find leads.""",
    verbose=True,
    allow_delegation=False,
    llm = llm,
    # Reusing the web_search tool from earlier, plus our new dynamic clustering tool
    tools=[web_search, dynamic_cluster] 
)

# 2. Define the Task
exhibitor_task = Task(
    description="""
    We are organizing a {event_type} ({event_category}) in {location}.
    
    Step 1: Use the 'web_search' tool to find 6 brands/vendors that recently had an exhibitor booth or presence at a similar {event_type}. 
    Step 2: Format those 6 companies into a strict JSON array string with the exact keys: "name", "description" (a 1-sentence summary of what they do).
    Step 3: Think of 3-4 appropriate categories for these vendors based on the {event_type}. (e.g., if it's a Tech conference: "Enterprise, Startup, Tools". If it's a Music Festival: "Food & Bev, Merch, Art Installations").
    Step 4: ACTION REQUIRED: You MUST use the 'Dynamic Clustering Engine' tool. Pass the JSON string from Step 2, PLUS the comma-separated target categories you created in Step 3, directly into this tool to categorize them. Do not skip this step.
    Step 5: Review the clustered output. Write a brief strategy note on which cluster we should prioritize selling to first for this specific event.
    
    CRITICAL INSTRUCTION: Do not stop early. Complete all steps and output the final categorized list.
    """,
    expected_output="""
    A structured report containing:
    1. Exhibitor Target List: The categorized list of the 6 vendors broken down by the dynamic categories you chose.
    2. Sales Strategy Note: A short paragraph explaining which category to target first and why.
    """,
    agent=exhibitor_agent
)

print("Exhibitor Agent and Task defined successfully!")




from crewai.tools import tool
import json

@tool("Venue Viability Engine")
def evaluate_venues(venues_data: str, expected_footfall: int, max_budget: float) -> str:
    """
    Takes a JSON string of venues and filters/scores them based on how well they 
    match the expected footfall and max budget constraints.
    """
    try:
        venues = json.loads(venues_data)
        expected_footfall = int(expected_footfall)
        max_budget = float(max_budget)
        
        viable_venues = []

        for venue in venues:
            capacity = int(venue.get('capacity', 0))
            cost = float(venue.get('estimated_cost', float('inf')))
            
            # HARD FILTERS: Discard if too small or too expensive
            if capacity < expected_footfall:
                venue['status'] = "REJECTED - Capacity too low"
                continue
            if cost > max_budget:
                venue['status'] = "REJECTED - Over budget"
                continue
                
            # SCORING: 
            score = 0
            
            # 1. Capacity Utilization (Goldilocks zone: 75% to 95% full)
            utilization = expected_footfall / capacity
            if 0.75 <= utilization <= 0.95:
                score += 50
            elif 0.50 <= utilization < 0.75:
                score += 25
                
            # 2. Cost Efficiency (Cheaper is better, up to 50 pts)
            cost_efficiency = 1 - (cost / max_budget)
            score += int(cost_efficiency * 50)
            
            venue['viability_score'] = score
            venue['status'] = "APPROVED"
            viable_venues.append(venue)
            
        # Sort by highest score first
        viable_venues = sorted(viable_venues, key=lambda x: x['viability_score'], reverse=True)
        
        if not viable_venues:
            return "WARNING: No venues met the strict capacity and budget constraints. You need to increase the budget or decrease the footfall."
            
        return json.dumps(viable_venues, indent=2)
        
    except Exception as e:
        return f"Error evaluating venues. Ensure input is valid JSON. Error: {str(e)}"

print("Venue Viability Engine loaded successfully!") 

# 1. Define the Agent
venue_agent = Agent(
    role='Head of Event Operations & Venue Sourcing',
    goal='Identify, evaluate, and secure the optimal venue based on capacity and budget constraints.',
    backstory="""You are a ruthless negotiator and logistical mastermind. You know that the venue 
    can make or break an event's profitability. You scour Cvent and Eventlocations.com to find spaces, 
    and you never accept a venue that exceeds the budget or can't comfortably fit the audience.""",
    verbose=True,
    allow_delegation=False,
    llm = llm,
    # Reusing the web_search tool, plus our new evaluation engine
    tools=[web_search, evaluate_venues] 
)

# 2. Define the Task
venue_task = Task(
    description="""
    We are organizing a {event_type} ({event_category}) focusing on "{event_topic}" in {location}. 
    Our maximum budget for the venue is ${max_budget}.
    Our expected footfall is {expected_footfall} attendees.
    
    Step 1: Use the 'web_search' tool to search the following domains: {search_domains} for "top {event_type} venues in {location} capable of hosting {expected_footfall} attendees". Find 4 potential venues.
    Step 2: Format those 4 venues into a strict JSON array string with the exact keys: "name", "capacity" (integer), and "estimated_cost" (integer). Make an educated estimate for capacity and cost based on your search if exact numbers aren't listed.
    Step 3: ACTION REQUIRED: You MUST use the 'Venue Viability Engine' tool. Pass the JSON string from Step 2, along with the {expected_footfall} and {max_budget}, directly into this tool to filter and score them. Do not skip this step.
    Step 4: Review the approved venues from the tool's output. Write a recommendation for the #1 venue, explaining why its capacity utilization and cost efficiency make it the best choice.
    
    CRITICAL INSTRUCTION: Complete all steps. If the tool warns that no venues fit the budget, state that clearly in your final report.
    """,
    expected_output="""
    A structured report containing:
    1. Evaluated Venue List: The ranked list of approved venues with their scores and capacities.
    2. Final Recommendation: A short paragraph pitching the winning venue based on logistics and financials.
    """,
    agent=venue_agent
)

print("Venue Agent and Task defined successfully!")



from crewai.tools import tool
import json

@tool("Community Categorization & Scoring Engine")
def analyze_communities(communities_data: str, event_niche: str) -> str:
    """
    Takes a JSON string of online communities and categorizes them by platform 
    (Discord, Slack, LinkedIn) and scores their relevance to the event niche.
    """
    try:
        communities = json.loads(communities_data)
        analyzed_communities = []

        for comm in communities:
            score = 0
            name = comm.get('name', '').lower()
            desc = comm.get('description', '').lower()
            platform = comm.get('platform', '').lower()
            
            # 1. Platform Prioritization (Hackathon doc emphasizes Discord initially)
            if 'discord' in platform:
                score += 30
            elif 'slack' in platform or 'linkedin' in platform:
                score += 20
            else:
                score += 10
                
            # 2. Niche Relevance
            if event_niche.lower() in name or event_niche.lower() in desc:
                score += 40
            else:
                score += 15 # Broad tech/business groups still get points
                
            # 3. Size/Activity (if available)
            members = int(comm.get('estimated_members', 0))
            if members > 10000:
                score += 30
            elif members > 1000:
                score += 15
                
            comm['gtm_priority_score'] = score
            
            # Categorize by Niche (e.g., 'Developers', 'Founders', 'Investors')
            if 'dev' in name or 'code' in name or 'hack' in desc:
                comm['audience_niche'] = 'Developers/Builders'
            elif 'founder' in name or 'startup' in desc or 'business' in desc:
                comm['audience_niche'] = 'Founders/Execs'
            else:
                comm['audience_niche'] = 'General Enthusiasts'
                
            analyzed_communities.append(comm)
            
        # Sort by highest priority first
        analyzed_communities = sorted(analyzed_communities, key=lambda x: x['gtm_priority_score'], reverse=True)
        return json.dumps(analyzed_communities, indent=2)
        
    except Exception as e:
        return f"Error analyzing communities. Ensure input is valid JSON. Error: {str(e)}"

print("Community Categorization Tool loaded successfully!")

# 1. Define the Agent
gtm_agent = Agent(
    role='Chief Marketing Officer & Community Hacker',
    goal='Identify high-leverage digital communities and draft a tactical Go-To-Market distribution plan.',
    backstory="""You are a growth-hacking genius. You know that traditional ads are expensive, 
    so you focus on grassroots community marketing. You infiltrate top-tier Discord servers, 
    Slack channels, and LinkedIn groups, crafting messaging that feels organic and valuable rather than spammy.""",
    verbose=True,
    allow_delegation=False,
    llm = llm,
    # Reusing the web_search tool, plus our new community analyzer
    tools=[web_search, analyze_communities] 
)

# 2. Define the Task
gtm_task = Task(
    description="""
    We need a GTM distribution plan for a {event_type} ({event_category}) focusing on "{event_topic}" and targeting {target_audience}.
    
    Step 1: Use the 'web_search' tool to find 5 specific online communities (look for a mix of Discord servers, Slack groups, subreddits, or LinkedIn groups) dedicated to "{event_topic}" or the target audience: {target_audience}. 
    Step 2: Format those 5 communities into a strict JSON array string with the exact keys: "name", "platform" (e.g., Discord, Slack, LinkedIn, Reddit), "description", and "estimated_members" (integer).
    Step 3: ACTION REQUIRED: You MUST use the 'Community Categorization & Scoring Engine' tool. Pass the JSON string from Step 2, along with the event niche "{event_topic}", directly into this tool to score and categorize them. Do not skip this step.
    Step 4: Review the prioritized list. Create a structured GTM Distribution Plan.
    Step 5: Write two distinct promotional messages: One casual, short message tailored for Discord/Slack/Reddit, and one professional, longer post tailored for a LinkedIn Group.
    
    CRITICAL INSTRUCTION: Complete all steps. Do not stop early.
    """,
    expected_output="""
    A structured report containing:
    1. Prioritized Community Targets: The ranked list of the 5 communities with their scores and niches.
    2. Distribution Plan: A brief strategy on how to sequence the promotion across these platforms.
    3. Messaging Drafts: 
       - Draft A: Discord/Slack/Reddit message (Casual, high energy).
       - Draft B: LinkedIn Group post (Professional, value-driven).
    """,
    agent=gtm_agent
)

print("Community & GTM Agent defined successfully!")



from crewai.tools import tool
import json

@tool("Schedule Conflict Detection Engine")
def detect_schedule_conflicts(proposed_schedule_json: str) -> str:
    """
    Takes a JSON string of a proposed schedule and checks for overlapping 
    room bookings or double-booked speakers.
    """
    try:
        schedule = json.loads(proposed_schedule_json)
        room_bookings = {}
        speaker_bookings = {}
        conflicts = []

        for session in schedule:
            room = session.get('room')
            speaker = session.get('speaker')
            time_slot = session.get('time_slot') # e.g., "10:00-11:00"
            session_name = session.get('session_title')

            # Check Room Conflicts
            room_key = f"{room}_{time_slot}"
            if room_key in room_bookings:
                conflicts.append(f"ROOM CONFLICT: {room} is double-booked at {time_slot} ({session_name} vs {room_bookings[room_key]}).")
            else:
                room_bookings[room_key] = session_name

            # Check Speaker Conflicts
            speaker_key = f"{speaker}_{time_slot}"
            if speaker_key in speaker_bookings:
                conflicts.append(f"SPEAKER CONFLICT: {speaker} is double-booked at {time_slot} ({session_name} vs {speaker_bookings[speaker_key]}).")
            else:
                speaker_bookings[speaker_key] = session_name

        if conflicts:
            return "SCHEDULE REJECTED. Conflicts found:\n" + "\n".join(conflicts) + "\nPlease revise the schedule and try again."
        else:
            return "SCHEDULE APPROVED. No room or speaker conflicts detected."
            
    except Exception as e:
        return f"Error parsing schedule. Ensure input is valid JSON array of sessions. Error: {str(e)}"

print("Conflict Detection Engine loaded successfully!")

# 1. Define the Agent
ops_agent = Agent(
    role='Director of Event Operations',
    goal='Build a seamless, conflict-free agenda and allocate physical resources efficiently.',
    backstory="""You are an operations mastermind. You handle the logistics of moving thousands 
    of people through different rooms throughout the day. You never finalize a schedule 
    without strictly checking for room overlaps and double-booked speakers.""",
    verbose=True,
    allow_delegation=False,
    llm = llm,
    tools=[detect_schedule_conflicts] 
)

# 2. Define the Task
ops_task = Task(
    description="""
    We need an opening-day schedule for a {event_type} ({event_category}) focusing on "{event_topic}" running from 9:00 AM to 1:00 PM.
    
    Available Rooms/Stages: 
    - Main Stage (Capacity 2000)
    - Workshop Room / Secondary Tent (Capacity 500)
    
    Sessions/Performances to Schedule:
    1. Headline Slot: "The Future of the Industry / Main Act" by Act A
    2. Panel/Supporting Slot: "Trends / Supporting Act" featuring Act B and Act C
    3. Workshop/Meetup Slot: "Deep Dive / VIP Meetup" by Act A
    
    Step 1: Draft a logical schedule assigning each session to a room/stage and a 1-hour time slot (e.g., 9:00-10:00). NOTE: Ensure Act A is not double-booked, and the Main Stage is not double-booked!
    Step 2: Format your drafted schedule into a strict JSON array string with the keys: "session_title", "speaker", "room", and "time_slot".
    Step 3: ACTION REQUIRED: Pass that JSON string directly into the 'Schedule Conflict Detection Engine' tool. 
    Step 4: If the tool returns "SCHEDULE REJECTED", you MUST fix the conflicts, update the JSON, and run the tool again. 
    Step 5: Once the tool returns "SCHEDULE APPROVED", output the final itinerary.
    
    CRITICAL INSTRUCTION: Do not stop until the tool explicitly approves the schedule.
    """,
    expected_output="""
    A structured report containing:
    1. The Final Approved Itinerary: A chronological list of sessions with their assigned times and rooms.
    2. Resource Utilization Note: A brief explanation of why you assigned specific sessions to the Main Stage vs the Secondary space.
    """,
    agent=ops_agent
)

print("Event Ops Agent defined successfully!")



from crewai import Process

# Combine all the agents you built into ONE team
master_event_crew = Crew(
    agents=[
        sponsor_agent, 
        speaker_agent, 
        exhibitor_agent, 
        venue_agent, 
        gtm_agent, 
        ops_agent
    ],
    tasks=[
        sponsor_task, 
        speaker_task, 
        exhibitor_task, 
        venue_task, 
        gtm_task, 
        ops_task
    ],
    process=Process.sequential, # They run in order, passing data down the chain
    verbose=True,
    memory=True,
    cache=True
)

# Kick off the entire autonomous system with your Master Payload
final_event_plan = master_event_crew.kickoff(inputs=event_context)

print("=== COMPLETE DOMAIN-AGNOSTIC EVENT PLAN ===")
print(final_event_plan)