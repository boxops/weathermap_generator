import pytest
from folium import Map
from folium.plugins import HeatMap


class TestInteractiveHeatmap:
    def test_prepare_heatmap(self, interactive_heatmap, sample_weather_data):
        interactive_heatmap.prepare_heatmap()
        assert len(interactive_heatmap.heat_data) == 1
        assert interactive_heatmap.heat_data[0] == [
            sample_weather_data["list"][0]["coord"]["lat"],
            sample_weather_data["list"][0]["coord"]["lon"],
            sample_weather_data["list"][0]["main"]["temp"] - 273.15,
        ]

    def test_create_map(self, interactive_heatmap):
        interactive_heatmap.create_map()
        assert isinstance(interactive_heatmap.m, Map)
        assert interactive_heatmap.m.location == [52.4862, -1.8904]

    def test_add_heatmap_layer(self, interactive_heatmap):
        interactive_heatmap.prepare_heatmap()
        interactive_heatmap.create_map()
        interactive_heatmap.add_heatmap_layer()

        # Check if HeatMap was added
        assert any(
            isinstance(child, HeatMap)
            for child in interactive_heatmap.m._children.values()
        )

    def test_add_interactive_markers(self, interactive_heatmap):
        interactive_heatmap.prepare_heatmap()
        interactive_heatmap.create_map()
        interactive_heatmap.add_interactive_markers()

        # Should have one marker for our sample data
        markers = [
            child
            for child in interactive_heatmap.m._children.values()
            if child.__class__.__name__ == "CircleMarker"
        ]
        assert len(markers) == 1

    def test_create_and_save_map(self, interactive_heatmap, tmp_path):
        test_output = tmp_path / "test_map.html"
        interactive_heatmap.prepare_heatmap()
        interactive_heatmap.create_map()
        interactive_heatmap.add_heatmap_layer()
        interactive_heatmap.add_interactive_markers()
        interactive_heatmap.create_and_save_map(str(test_output))

        assert test_output.exists()
        with open(test_output) as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "Birmingham" in content

    def test_run_method(self, interactive_heatmap, tmp_path):
        test_output = tmp_path / "test_map.html"
        interactive_heatmap.run(str(test_output))
        assert test_output.exists()
