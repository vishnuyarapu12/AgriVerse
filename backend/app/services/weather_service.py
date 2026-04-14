"""
Farm weather using Open-Meteo (no API key).
Docs: https://open-meteo.com/en/docs

Current conditions: temperature_2m, wind_speed_10m (km/h), weather_code (WMO).
"""
import logging
from typing import Any, Dict, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

# Open-Meteo forecast API — current weather block
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Default: Hyderabad, Telangana (when lat/lon omitted)
DEFAULT_LAT = 17.3850
DEFAULT_LON = 78.4867


def _is_rain_or_storm_code(code: Optional[int]) -> bool:
    """
    WMO codes used by Open-Meteo for precipitation / storms.
    See: https://open-meteo.com/en/docs#api_form
    """
    if code is None:
        return False
    # Drizzle, rain, freezing rain, showers, thunderstorm, snow+rain mix where relevant
    if 51 <= code <= 67:
        return True
    if 80 <= code <= 82:
        return True
    if 95 <= code <= 99:
        return True
    return False


def _spray_advice(wind_kmh: float, weather_code: Optional[int]) -> str:
    """
    Farmer-friendly rules (order: rain first, then wind).
    - Rain / storm code → no spray
    - Wind speed > 20 km/h (Open-Meteo default unit) → high wind
    - Else safe
    """
    if _is_rain_or_storm_code(weather_code):
        return "Do NOT spray pesticides (rain expected)"
    if wind_kmh > 20:
        return "Avoid spraying pesticides (high wind)"
    return "Safe to spray"


def _get_ideal_spray_window(hourly_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze 24-hour hourly forecast to find ideal spraying window.
    Returns: {ideal_hour, ideal_period, warning_message}
    
    Ideal conditions:
    - No rain (weather_code not in rain codes)
    - Wind speed < 15 km/h (safe for spray drift)
    - Temperature > 15°C (optimal for pesticide effectiveness)
    - Prefer early morning (6-10 AM) for minimal drift
    """
    if not hourly_data or not hourly_data.get("times"):
        return {
            "ideal_hour": None,
            "ideal_period": "Unable to determine",
            "warning_message": "Insufficient forecast data",
            "next_safe_window": None
        }
    
    times = hourly_data["times"]
    temps = hourly_data.get("temperature_2m", [])
    winds = hourly_data.get("wind_speed_10m", [])
    weather_codes = hourly_data.get("weather_code", [])
    
    ideal_hours = []
    has_rain_today = False
    rain_start_hour = None
    rain_end_hour = None
    
    # Scan 24-hour window starting now
    for i in range(min(24, len(times))):
        temp = temps[i] if i < len(temps) else 0
        wind = winds[i] if i < len(winds) else 0
        code = weather_codes[i] if i < len(weather_codes) else None
        
        has_rain = _is_rain_or_storm_code(code)
        if has_rain and rain_start_hour is None:
            has_rain_today = True
            rain_start_hour = i
        if has_rain_today and not has_rain and rain_start_hour is not None:
            rain_end_hour = i
        
        # Ideal spray conditions
        is_safe = (
            not has_rain
            and wind < 15
            and temp > 15
        )
        
        if is_safe:
            ideal_hours.append({
                "hour": i,
                "time": times[i],
                "wind": wind,
                "temp": temp
            })
    
    result = {
        "has_rain_today": has_rain_today,
        "rain_start_hour": rain_start_hour,
        "rain_end_hour": rain_end_hour,
    }
    
    if ideal_hours:
        # Prefer early morning window (6-11 AM = hours 6-11)
        morning_window = [h for h in ideal_hours if 6 <= h["hour"] <= 11]
        if morning_window:
            best = morning_window[0]
            result["ideal_hour"] = best["hour"]
            result["ideal_period"] = f"{best['hour']:02d}:00"
            result["ideal_hour_display"] = f"{best['hour']}:00 AM"
            result["wind_at_ideal"] = best["wind"]
            result["temp_at_ideal"] = best["temp"]
            result["warning_message"] = None
        else:
            # Use first available safe hour
            best = ideal_hours[0]
            result["ideal_hour"] = best["hour"]
            result["ideal_period"] = f"{best['hour']:02d}:00"
            result["ideal_hour_display"] = f"{best['hour']}:00"
            result["wind_at_ideal"] = best["wind"]
            result["temp_at_ideal"] = best["temp"]
            result["warning_message"] = "First safe window outside recommended morning hours"
    else:
        result["ideal_hour"] = None
        result["ideal_period"] = None
        result["ideal_hour_display"] = None
        if has_rain_today:
            result["warning_message"] = "Heavy rain/wind throughout day - postpone spraying"
        else:
            result["warning_message"] = "No ideal conditions found in next 24 hours"
    
    return result


def resolve_coordinates(lat: Optional[float], lon: Optional[float]) -> Tuple[float, float, bool]:
    """
    If either lat or lon is missing, use Hyderabad defaults.
    Returns (lat, lon, used_default).
    """
    if lat is None or lon is None:
        logger.info("Weather: lat/lon incomplete — using default Hyderabad (%.4f, %.4f)", DEFAULT_LAT, DEFAULT_LON)
        return DEFAULT_LAT, DEFAULT_LON, True
    return lat, lon, False


async def fetch_farm_weather(lat: Optional[float], lon: Optional[float]) -> Dict[str, Any]:
    """
    Fetch current AND 24-hour forecast from Open-Meteo.
    Provides smart spraying window recommendations.
    Raises ValueError on bad response; lets httpx raise on HTTP errors (caught in route).
    """
    use_lat, use_lon, _ = resolve_coordinates(lat, lon)

    params = {
        "latitude": use_lat,
        "longitude": use_lon,
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,wind_speed_10m,weather_code",
        "forecast_days": 1,
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    cur = payload.get("current") or {}
    hourly = payload.get("hourly") or {}
    
    try:
        temp = float(cur["temperature_2m"])
        wind = float(cur["wind_speed_10m"])
        wcode = cur.get("weather_code")
        if wcode is not None:
            wcode = int(wcode)
    except (KeyError, TypeError, ValueError) as e:
        logger.exception("Open-Meteo parse error: %s", e)
        raise ValueError("Invalid weather data from provider") from e

    advice = _spray_advice(wind, wcode)
    
    # Get smart spraying window recommendation
    spray_window = _get_ideal_spray_window(hourly)
    
    logger.info(
        "Open-Meteo (%.4f, %.4f): %.1f°C, wind=%.1f km/h, code=%s -> %s. "
        "Ideal spray: %s",
        use_lat,
        use_lon,
        temp,
        wind,
        wcode,
        advice,
        spray_window.get("ideal_hour_display", "Unknown"),
    )

    return {
        "temperature": round(temp, 1),
        "wind_speed": round(wind, 1),
        "advice": advice,
        "spray_window": spray_window,
    }
