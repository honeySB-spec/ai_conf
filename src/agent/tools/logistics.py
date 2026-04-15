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
            
            utilization = expected_footfall / capacity if capacity > 0 else 0
            if 0.75 <= utilization <= 0.95:
                score += 50
            elif 0.50 <= utilization < 0.75:
                score += 25
                
            # Cost Efficiency (Cheaper is better, up to 50 pts)
            cost_efficiency = 1 - (cost / max_budget)
            score += int(cost_efficiency * 50)
            
            venue['viability_score'] = score
            venue['status'] = "APPROVED"
            viable_venues.append(venue)
            
        viable_venues = sorted(viable_venues, key=lambda x: x['viability_score'], reverse=True)
        
        if not viable_venues:
            return "WARNING: No venues met the strict capacity and budget constraints. You need to increase the budget or decrease the footfall."
            
        return json.dumps(viable_venues, indent=2)
        
    except Exception as e:
        return f"Error evaluating venues. Ensure input is valid JSON. Error: {str(e)}"

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
            if not room or not time_slot:
                continue

            room_key = f"{room}_{time_slot}"
            if room_key in room_bookings:
                conflicts.append(f"ROOM CONFLICT: {room} is double-booked at {time_slot} ({session_name} vs {room_bookings[room_key]}).")
            else:
                room_bookings[room_key] = session_name

            # Check Speaker Conflicts
            if speaker:
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
