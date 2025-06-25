import pytest
from unittest.mock import AsyncMock, patch
from app.services.geographic_analysis_service import GeographicAnalysis
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_same_country():
    geo = GeographicAnalysis()
    result = await geo.Is_the_country_same_as_payment_method("US", "US")
    assert result == ("from the same country", True)

@pytest.mark.asyncio
async def test_different_country():
    geo = GeographicAnalysis()
    result = await geo.Is_the_country_same_as_payment_method("US", "CA")
    assert result == ("different countries", False)

@pytest.mark.asyncio
async def test_high_risk_country():
    geo = GeographicAnalysis()
    result = await geo.is_high_risk_country("RU")
    assert result == ("High_risk_country", True)

@pytest.mark.asyncio
async def test_low_risk_country():
    geo = GeographicAnalysis()
    result = await geo.is_high_risk_country("DE")
    assert result == ("not a high risk country", False)

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_ip_to_country_success(mock_get):
    mock_response = AsyncMock()
    mock_response.json.return_value = {"status": "success", "countryCode": "JP"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    geo = GeographicAnalysis()
    country = await geo.get_country_from_ip("192.0.2.1")
    assert country == "JP"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_ip_to_country_failure(mock_get):
    mock_response = AsyncMock()
    mock_response.json.return_value = {"status": "fail"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    geo = GeographicAnalysis()
    country = await geo.get_country_from_ip("192.0.2.1")
    assert country == "Unknown"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_ip_service_unavailable(mock_get):
    mock_get.side_effect = Exception("Connection failed")
    geo = GeographicAnalysis()
    with pytest.raises(HTTPException) as exc:
        await geo.get_country_from_ip("192.0.2.1")
    assert exc.value.status_code == 500