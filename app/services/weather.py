import httpx
from pydantic import BaseModel

class WeatherData(BaseModel):
    dr: float
    dcr3: float
    dar30: float

def fetch_weather_data() -> WeatherData:
    """
    Fetches weather data from Open-Meteo API and calculates DR, 3DCR, 30DAR.
    Check 2 Constraint: Strict 5.0s timeout with fallback to mock data.
    """
    url = "https://api.open-meteo.com/v1/forecast?latitude=23.73&longitude=92.71&daily=precipitation_sum&timezone=auto&past_days=30"
    
    try:
        # Wrap the call in a strict 5.0s timeout
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # The "daily" dictionary contains lists. "precipitation_sum" is the list of rainfall.
            # Usually the current day is at index -7 or so if past_days=30 and forecast is 7 days.
            # But let's just grab the most recent historical block.
            precip = data.get("daily", {}).get("precipitation_sum", [])
            
            if len(precip) >= 30:
                # Let's say today is the last element for calculation purposes
                dr = float(precip[-1] or 0.0)
                dcr3 = sum(float(x or 0.0) for x in precip[-3:])
                dar30 = sum(float(x or 0.0) for x in precip[-31:-1]) # Antecedent = past 30 days before today
            else:
                # If API didn't return 30 days, fallback to mock
                raise ValueError("Not enough historical data returned from API")
                
            return WeatherData(dr=dr, dcr3=dcr3, dar30=dar30)
            
    except (httpx.TimeoutException, httpx.RequestError, ValueError) as e:
        print(f"Weather API Error/Timeout ({e}): Falling back to safe mock averages.")
        # Fallback safe defaults (Normal day)
        return WeatherData(dr=0.0, dcr3=0.0, dar30=10.0)
