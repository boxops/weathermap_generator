import pytest
import json
from unittest.mock import patch, mock_open
from src.weather_map import WeatherDataFetcher


class TestWeatherDataFetcher:
    def test_fetch_data_success(self, mock_weather_api, weather_data_fetcher):
        weather_data_fetcher.fresh_data = True
        result = weather_data_fetcher.fetch_data()

        # Verify the API was called with correct URL
        mock_weather_api.assert_called_once()
        called_url = mock_weather_api.call_args[0][0]
        assert "openweathermap.org" in called_url
        assert "lat=52.4862" in called_url
        assert "lon=-1.8904" in called_url

        # Verify we got our mock data
        assert result == mock_weather_api.return_value.json.return_value
        assert weather_data_fetcher.data == result

    def test_fetch_data_failure(self, mocker, weather_data_fetcher):
        mocker.patch("requests.get", side_effect=Exception("API Error"))
        weather_data_fetcher.fresh_data = True

        with pytest.raises(
            RuntimeError, match="Failed to fetch data from OpenWeatherMap API"
        ):
            weather_data_fetcher.fetch_data()

    def test_init_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENWEATHERMAP_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OpenWeatherMap API key is not set"):
            WeatherDataFetcher("test.json", "52.4862", "-1.8904")

    def test_open_data_success(self, weather_data_fetcher, sample_weather_data):
        data = weather_data_fetcher.open_data()
        assert data == sample_weather_data

    def test_open_data_file_not_found(self, tmp_path, monkeypatch):
        # Mock the API key environment variable
        monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "test_api_key")
        non_existent_file = tmp_path / "nonexistent.json"
        fetcher = WeatherDataFetcher(
            file=non_existent_file,
            latitude="52.4862",
            longitude="-1.8904",
            fresh_data=False,
        )
        with pytest.raises(FileNotFoundError):
            fetcher.open_data()

    def test_save_data(self, weather_data_fetcher, sample_weather_data, tmp_path):
        test_file = tmp_path / "test_save.json"
        weather_data_fetcher.file = test_file
        weather_data_fetcher.data = sample_weather_data
        weather_data_fetcher.save_data()

        assert test_file.exists()
        with open(test_file) as f:
            assert json.load(f) == sample_weather_data

    def test_debug_output(self, capsys, weather_data_fetcher):
        weather_data_fetcher.debug_enabled = True
        test_message = "Test debug message"
        weather_data_fetcher.debug(test_message)

        captured = capsys.readouterr()
        assert test_message in captured.out
