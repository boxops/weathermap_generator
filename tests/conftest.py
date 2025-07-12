import pytest
import json
import os
from src.weather_map import WeatherDataFetcher, InteractiveHeatmap


@pytest.fixture
def sample_weather_data():
    return {
        "list": [
            {
                "coord": {"lat": 52.4862, "lon": -1.8904},
                "main": {"temp": 285.15, "humidity": 75},
                "weather": [{"description": "clear sky"}],
                "name": "Birmingham",
            }
        ]
    }


@pytest.fixture
def mock_weather_api(mocker):
    """Fixture to mock the OpenWeatherMap API responses"""
    mock_response = {
        "list": [
            {
                "coord": {"lat": 52.4862, "lon": -1.8904},
                "main": {"temp": 285.15, "humidity": 75},
                "weather": [{"description": "clear sky"}],
                "name": "Birmingham"
            }
        ]
    }
    mock = mocker.patch('requests.get')
    mock.return_value.json.return_value = mock_response
    return mock


@pytest.fixture
def mock_data_file(tmp_path, sample_weather_data):
    file = tmp_path / "weather.json"
    with open(file, "w") as f:
        json.dump(sample_weather_data, f)
    return file


@pytest.fixture
def weather_data_fetcher(mock_data_file):
    return WeatherDataFetcher(
        file=mock_data_file,
        latitude="52.4862",
        longitude="-1.8904",
        fresh_data=False,
        debug=False,
    )


@pytest.fixture
def interactive_heatmap(weather_data_fetcher):
    return InteractiveHeatmap(weather_data_fetcher)
