import os
import json
import requests
from crewai.tools import tool

# Ensure RapidAPI explicitly expects OS env directly if desired, but we check os.environ.
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "1e538f0d54msh8be9c8bd60615c3p1801a4jsnf5ed6c34dd6a")

@tool("LinkedIn Profile Fetcher")
def fetch_linkedin_data(linkedin_url: str) -> str:
    """
    Fetches real-time structured profile data (experience, followers, headline) 
    from a LinkedIn URL using a RapidAPI wrapper. ONLY pass valid linkedin.com/in/ URLs.
    """
    api_endpoint = "https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead"
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }
    
    querystring = {"linkedin_url": linkedin_url}
    
    try:
        response = requests.get(api_endpoint, headers=headers, params=querystring)
        
        if response.status_code == 200:
            data = response.json()
            
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
            
            # Categorize by Niche
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
