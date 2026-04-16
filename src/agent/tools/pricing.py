import json
from crewai.tools import tool

@tool("Predictive Pricing & Attendance Model")
def predict_pricing_and_attendance(event_type: str, expected_footfall: int, location: str) -> str:
    """
    Simulates predicting optimal ticket prices and attendance based on event data.
    
    Args:
        event_type (str): The type of the event (e.g. Conference, Music Festival).
        expected_footfall (int): The target audience size.
        location (str): The geographic location of the event.
        
    Returns:
        str: A JSON formatted string containing the optimal ticket tiers, prices, 
             conversion rate predictions, and expected actual attendance.
    """
    # Base logic to simulate realistic pricing tiers depending on event size
    base_price = 100 if expected_footfall < 500 else 250
    if "Conference" in event_type or "Corporate" in event_type:
        base_price *= 2
        
    # Generate pricing tiers
    early_bird = int(base_price * 0.7)
    vip = int(base_price * 3.5)
    
    # Simulate conversion rates
    conversion_rates = {
        "early_bird": "35%",
        "standard": "50%",
        "vip": "15%"
    }
    
    # Simulate attendance variance based on marketing efficiency (mocked)
    expected_actual = int(expected_footfall * 0.95)
    
    result = {
        "recommended_tiers": {
            "early_bird": {"price": f"${early_bird}", "allocation": conversion_rates["early_bird"]},
            "standard": {"price": f"${base_price}", "allocation": conversion_rates["standard"]},
            "vip": {"price": f"${vip}", "allocation": conversion_rates["vip"]}
        },
        "expected_attendance": expected_actual,
        "revenue_projection_estimate": (early_bird * expected_actual * 0.35) + \
                                       (base_price * expected_actual * 0.50) + \
                                       (vip * expected_actual * 0.15)
    }
    
    return json.dumps(result, indent=2)
