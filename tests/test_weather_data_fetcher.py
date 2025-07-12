import pytest
import json
from unittest.mock import patch, mock_open
from src.weather_map import WeatherDataFetcher, InteractiveHeatmap


class TestWeatherDataFetcher:
    def test_init_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENWEATHERMAP_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OpenWeatherMap API key is not set"):
            WeatherDataFetcher("test.json", "52.4862", "-1.8904")

    def test_open_data_success(self, weather_data_fetcher, sample_weather_data):
        data = weather_data_fetcher.open_data()
        assert data == sample_weather_data

    def test_open_data_file_not_found(self, tmp_path):
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

    @patch("requests.get")
    def test_fetch_data_success(
        self, mock_get, weather_data_fetcher, sample_weather_data
    ):
        mock_get.return_value.json.return_value = sample_weather_data
        weather_data_fetcher.fresh_data = True

        result = weather_data_fetcher.fetch_data()
        assert result == sample_weather_data
        assert weather_data_fetcher.data == sample_weather_data

    @patch("requests.get")
    def test_fetch_data_failure(self, mock_get, weather_data_fetcher):
        mock_get.side_effect = Exception("API Error")
        weather_data_fetcher.fresh_data = True

        with pytest.raises(
            RuntimeError, match="Failed to fetch data from OpenWeatherMap API"
        ):
            weather_data_fetcher.fetch_data()

    def test_debug_output(self, capsys, weather_data_fetcher):
        weather_data_fetcher.debug_enabled = True
        test_message = "Test debug message"
        weather_data_fetcher.debug(test_message)

        captured = capsys.readouterr()
        assert test_message in captured.out
