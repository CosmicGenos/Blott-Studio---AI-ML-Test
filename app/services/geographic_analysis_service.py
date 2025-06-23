
import httpx
from fastapi import HTTPException


class GeographicAnalysis:

    async def Is_the_country_same_as_payment_method(self, country1: str, country2: str) -> tuple[str, bool]:
        if country1.strip().lower() == country2.strip().lower():
            return "from the same country", True
        else:
            return "different countries", False

    async def get_country_from_ip(self,ip_address: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"http://ip-api.com/json/{ip_address}")
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "success":
                    return data.get("countryCode", "Unknown")
                else:
                    return "Unknown"
            except Exception:
                raise HTTPException(status_code=500, detail="Geolocation service unavailable")

    async def is_high_risk_country(self, country_code: str) -> tuple[str, bool]:
        HIGH_RISK_COUNTRIES = ['RU', 'IR', 'KP', 'VE', 'MM']
        if country_code.strip().upper() in HIGH_RISK_COUNTRIES:
            return "High_risk_country", True
        else:
            return "not a high risk country", False

