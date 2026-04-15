from crewai.tools import tool
import json

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
