import os
from crewai import Agent, Task, Crew, Process, LLM
from src.agent.tools import web_search, fetch_linkedin_data, analyze_communities, evaluate_venues, dynamic_cluster, detect_schedule_conflicts, score_speakers, score_sponsors, predict_pricing_and_attendance

class EventPlanningCrew:
    def __init__(self):
        # Initialize the LLM config as used in test.py
        self.llm = LLM(
            model="openrouter/google/gemini-2.0-flash-001",
            api_key=os.environ.get("OPENROUTER_API_KEY")
        )
        self.agents = self.setup_agents()
        self.tasks = []
        
    def setup_agents(self):
        sponsor_agent = Agent(
            role='VP of Corporate Partnerships',
            goal='Identify, score, and draft proposals for potential event sponsors.',
            backstory="""You are an expert in B2B event marketing. You know that finding the right 
            sponsor is about data, not guessing. You look for companies that have recently sponsored 
            similar events, score them based on fit, and write highly persuasive outreach proposals.""",
            verbose=True,
            allow_delegation=False,
            tools=[web_search, score_sponsors],
            llm=self.llm
        )

        speaker_agent = Agent(
            role='Head of Content & Speaker Relations',
            goal='Discover top-tier subject matter experts using real-time LinkedIn data and map them to agenda topics.',
            backstory="""You are a visionary event producer. You don't guess a speaker's influence; 
            you pull their actual real-time LinkedIn data to see their exact follower count and experience 
            before making a decision.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[web_search, fetch_linkedin_data, score_speakers] 
        )

        exhibitor_agent = Agent(
            role='Director of Exhibition Sales',
            goal='Identify past exhibitors/vendors from similar events and cluster them into actionable sales categories.',
            backstory="""You are a tactical sales director. You know that selling booth or tent space requires targeting the right mix of vendors tailored to the specific event type. You systematically scrape competitor events to find leads.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[web_search, dynamic_cluster] 
        )

        venue_agent = Agent(
            role='Head of Event Operations & Venue Sourcing',
            goal='Identify, evaluate, and secure the optimal venue based on capacity and budget constraints.',
            backstory="""You are a ruthless negotiator and logistical mastermind. You know that the venue 
            can make or break an event's profitability. You scour Cvent and Eventlocations.com to find spaces, 
            and you never accept a venue that exceeds the budget or can't comfortably fit the audience.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[web_search, evaluate_venues] 
        )

        gtm_agent = Agent(
            role='Chief Marketing Officer & Community Hacker',
            goal='Identify high-leverage digital communities and draft a tactical Go-To-Market distribution plan.',
            backstory="""You are a growth-hacking genius. You focus on grassroots community marketing. You infiltrate top-tier Discord servers, 
            Slack channels, and LinkedIn groups, crafting messaging that feels organic and valuable rather than spammy.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[web_search, analyze_communities] 
        )

        ops_agent = Agent(
            role='Director of Event Operations',
            goal='Build a seamless, conflict-free agenda and allocate physical resources efficiently.',
            backstory="""You are an operations mastermind. You handle the logistics of moving thousands 
            of people through different rooms throughout the day. You never finalize a schedule 
            without strictly checking for room overlaps and double-booked speakers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[detect_schedule_conflicts] 
        )

        pricing_agent = Agent(
            role='Head of Revenue & Ticketing Strategy',
            goal='Model the relationship between ticket pricing tiers and conversion rates to predict optimal pricing and attendance.',
            backstory="""You are a data-driven revenue strategist. You analyze historical event footprints to predict the perfect ticket pricing tiers. You utilize models to maximize revenue without sacrificing target attendance goals.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[predict_pricing_and_attendance]
        )

        return {
            "sponsor": sponsor_agent,
            "speaker": speaker_agent,
            "exhibitor": exhibitor_agent,
            "venue": venue_agent,
            "pricing": pricing_agent,
            "gtm": gtm_agent,
            "ops": ops_agent
        }

    def setup_tasks(self, context: dict, task_callback=None):
        sponsor_task = Task(
            description=f"""
            We are organizing a {context['event_type']} ({context['event_category']}) in {context['location']} focusing on "{context['event_topic']}" targeting {context['target_audience']}.
            
            Step 1: Use the web search tool to find 4 brands that have recently sponsored similar {context['event_type']}s in the {context['event_category']} space targeting {context['target_audience']} in or near {context['location']}.
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
            agent=self.agents["sponsor"],
            callback=task_callback
        )

        speaker_task = Task(
            description=f"""
            We are organizing a {context['event_type']} ({context['event_category']}) focusing on "{context['event_topic']}".
            
            Step 1: Use the 'web_search' tool to find the names and exact LinkedIn Profile URLs of 3 notable thought leaders, artists, or figures relevant to "{context['event_topic']}" or {context['event_category']}. (Look for URLs starting with https://www.linkedin.com/in/).
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
            agent=self.agents["speaker"],
            callback=task_callback
        )

        exhibitor_task = Task(
            description=f"""
            We are organizing a {context['event_type']} ({context['event_category']}) in {context['location']}.
            
            Step 1: Use the 'web_search' tool to find 6 brands/vendors that recently had an exhibitor booth or presence at a similar {context['event_type']}. 
            Step 2: Format those 6 companies into a strict JSON array string with the exact keys: "name", "description" (a 1-sentence summary of what they do).
            Step 3: Think of 3-4 appropriate categories for these vendors based on the {context['event_type']}. (e.g., if it's a Tech conference: "Enterprise, Startup, Tools". If it's a Music Festival: "Food & Bev, Merch, Art Installations").
            Step 4: ACTION REQUIRED: You MUST use the 'Dynamic Clustering Engine' tool. Pass the JSON string from Step 2, PLUS the comma-separated target categories you created in Step 3, directly into this tool to categorize them. Do not skip this step.
            Step 5: Review the clustered output. Write a brief strategy note on which cluster we should prioritize selling to first for this specific event.
            
            CRITICAL INSTRUCTION: Do not stop early. Complete all steps and output the final categorized list.
            """,
            expected_output="""
            A structured report containing:
            1. Exhibitor Target List: The categorized list of the 6 vendors broken down by the dynamic categories you chose.
            2. Sales Strategy Note: A short paragraph explaining which category to target first and why.
            """,
            agent=self.agents["exhibitor"],
            callback=task_callback
        )

        venue_task = Task(
            description=f"""
            We are organizing a {context['event_type']} ({context['event_category']}) focusing on "{context['event_topic']}" in {context['location']}. 
            Our maximum budget for the venue is ${context['max_budget']}.
            Our expected footfall is {context['expected_footfall']} attendees.
            
            Step 1: Use the 'web_search' tool to search the following domains: {context['search_domains']} for "top {context['event_type']} venues in {context['location']} capable of hosting {context['expected_footfall']} attendees". Find 4 potential venues.
            Step 2: Format those 4 venues into a strict JSON array string with the exact keys: "name", "capacity" (integer), and "estimated_cost" (integer). Make an educated estimate for capacity and cost based on your search if exact numbers aren't listed.
            Step 3: ACTION REQUIRED: You MUST use the 'Venue Viability Engine' tool. Pass the JSON string from Step 2, along with the {context['expected_footfall']} and {context['max_budget']}, directly into this tool to filter and score them. Do not skip this step.
            Step 4: Review the approved venues from the tool's output. Write a recommendation for the #1 venue, explaining why its capacity utilization and cost efficiency make it the best choice.
            
            CRITICAL INSTRUCTION: Complete all steps. If the tool warns that no venues fit the budget, state that clearly in your final report.
            """,
            expected_output="""
            A structured report containing:
            1. Evaluated Venue List: The ranked list of approved venues with their scores and capacities.
            2. Final Recommendation: A short paragraph pitching the winning venue based on logistics and financials.
            """,
            agent=self.agents["venue"],
            callback=task_callback
        )

        pricing_task = Task(
            description=f"""
            We are determining the financial model for a {context['event_type']} focusing on "{context['event_topic']}" in {context['location']} targeting {context['expected_footfall']} attendees.
            
            Step 1: ACTION REQUIRED: You MUST use the 'Predictive Pricing & Attendance Model' tool. Pass the event_type ({context['event_type']}), expected_footfall ({context['expected_footfall']}), and location ({context['location']}) directly into this tool to simulate optimal pricing. Do not skip this step.
            Step 2: Review the output of the pricing model, which includes recommended tiers (price and allocation), expected actual attendance, and revenue projections.
            Step 3: Write a 2-paragraph revenue strategy explaining the relationship between the pricing tiers, the conversion rates, and the expected attendance, ensuring it ties back to the total event metrics.

            CRITICAL INSTRUCTION: Complete all steps and provide the final strategy.
            """,
            expected_output="""
            A structured report containing:
            1. Pricing Tiers & Simulation: A breakdown of the recommended tiers (Early Bird, Standard, VIP).
            2. Revenue Strategy: A clear explanation of why these prices will maximize attendance and revenue.
            """,
            agent=self.agents["pricing"],
            callback=task_callback
        )

        gtm_task = Task(
            description=f"""
            We need a GTM distribution plan for a {context['event_type']} ({context['event_category']}) focusing on "{context['event_topic']}" and targeting {context['target_audience']}.
            
            Step 1: Use the 'web_search' tool to find 5 specific online communities (look for a mix of Discord servers, Slack groups, subreddits, or LinkedIn groups) dedicated to "{context['event_topic']}" or the target audience: {context['target_audience']}. 
            Step 2: Format those 5 communities into a strict JSON array string with the exact keys: "name", "platform" (e.g., Discord, Slack, LinkedIn, Reddit), "description", and "estimated_members" (integer).
            Step 3: ACTION REQUIRED: You MUST use the 'Community Categorization & Scoring Engine' tool. Pass the JSON string from Step 2, along with the event niche "{context['event_topic']}", directly into this tool to score and categorize them. Do not skip this step.
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
            agent=self.agents["gtm"],
            callback=task_callback
        )

        ops_task = Task(
            description=f"""
            We need an opening-day schedule for a {context['event_type']} ({context['event_category']}) focusing on "{context['event_topic']}" running from 9:00 AM to 1:00 PM.
            
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
            agent=self.agents["ops"],
            callback=task_callback
        )

        self.tasks = [sponsor_task, speaker_task, exhibitor_task, venue_task, pricing_task, gtm_task, ops_task]
        return self.tasks

    def kickoff(self, context: dict, task_callback=None) -> str:
        tasks = self.setup_tasks(context, task_callback)
        
        # When creating the Crew, pass along the task_callback so we can stream output when tasks finish
        crew_kwargs = {
            "agents": list(self.agents.values()),
            "tasks": tasks,
            "process": Process.sequential,
            "verbose": True,
            "memory": False,
            "cache": True,
            
        }
        if task_callback:
            crew_kwargs["task_callback"] = task_callback
            
        master_event_crew = Crew(**crew_kwargs)
        
        # CrewAI kickoff natively returns a structured Output object or string
        final_crew_output = master_event_crew.kickoff()
        
        full_plan = ["# 📋 Master Event Plan"]
        
        # Aggregate output from all tasks
        for task in tasks:
            if hasattr(task, 'output') and task.output:
                role = task.agent.role if task.agent else "Agent"
                full_plan.append(f"## {role} Report\n{str(task.output)}")
        
        if len(full_plan) > 1:
            return "\n\n---\n\n".join(full_plan)
            
        return str(final_crew_output)
