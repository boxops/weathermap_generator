import requests
import folium
from folium.plugins import HeatMap
from dotenv import load_dotenv
from pprint import pprint
import os
import json

load_dotenv()


class WeatherDataFetcher:
    """Class to fetch weather data from OpenWeatherMap API."""

    def __init__(self, file, latitude, longitude, fresh_data=False, debug=False):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenWeatherMap API key is not set. Please set it in the .env file."
            )
        self.file = file
        self.latitude = latitude
        self.longitude = longitude
        self.debug_enabled = debug
        self.fresh_data = fresh_data

    def fetch_data(self):
        """Fetches weather data for cities in the West Midlands."""
        if not self.fresh_data:
            self.debug(f"Using existing data from {self.file}")
            return self.open_data()
        try:
            self.debug(
                f"Fetching fresh data from OpenWeatherMap API for lat: {self.latitude}, lon: {self.longitude}"
            )
            url = f"https://api.openweathermap.org/data/2.5/find?lat={self.latitude}&lon={self.longitude}&cnt=50&appid={self.api_key}"
            self.data = requests.get(url).json()
            self.debug(f"Fetched data: {self.data}")
            self.save_data()
            return self.data
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from OpenWeatherMap API: {e}")

    def save_data(self):
        """Saves weather data to a JSON file."""
        try:
            with open(self.file, "w") as f:
                json.dump(self.data, f, indent=4)
            self.debug(f"Data saved to {self.file}")
        except IOError as e:
            raise RuntimeError(f"Failed to save data to {self.file}: {e}")

    def open_data(self):
        """Fetches and returns weather data for the West Midlands."""
        try:
            with open(self.file, "r") as f:
                data = json.load(f)
            self.debug(f"Data loaded from {self.file}")
            self.debug(f"Data content: {data}")
            return data
        except IOError:
            self.debug(f"{self.file} not found, fetching new data.")
            raise FileNotFoundError(f"{self.file} not found. Please fetch data first.")

    def debug(self, message):
        """Debugging method to print messages."""
        if self.debug_enabled:
            pprint(f"[DEBUG] {message}")


class InteractiveHeatmap:
    """Class to create an interactive heatmap with weather data."""

    def __init__(self, data_fetcher, debug=False):
        self.data_fetcher = data_fetcher
        self.debug_enabled = debug
        self.heat_data = []
        self.data = self.data_fetcher.fetch_data()
        self.m = None

    def prepare_heatmap(self):
        """Prepare heatmap data: [[lat, lon, temperature]]"""
        self.heat_data = []
        for city in self.data["list"]:
            lat, lon = city["coord"]["lat"], city["coord"]["lon"]
            temp_celsius = city["main"]["temp"] - 273.15
            self.heat_data.append([lat, lon, temp_celsius])
            self.debug(
                f"Added heat data for {city['name']}: [{lat}, {lon}, {temp_celsius:.1f}]"
            )

    def create_map(self):
        """Creates the base folium map."""
        self.m = folium.Map(
            location=[52.4862, -1.8904], zoom_start=9, tiles="CartoDB dark_matter"
        )
        self.debug("Base map created.")

    def add_heatmap_layer(self):
        """Adds a heatmap layer to the map."""
        if not self.m:
            raise ValueError("Map not created. Call create_map() first.")

        HeatMap(
            self.heat_data,
            name="Temperature Heatmap",
            gradient={0.2: "blue", 0.5: "lime", 0.8: "red"},
            radius=25,
            blur=15,
            min_opacity=0.5,
        ).add_to(self.m)
        self.debug("Heatmap layer added.")

    def add_interactive_markers(self):
        """Adds interactive markers with popups to the map."""
        if not self.m:
            raise ValueError("Map not created. Call create_map() first.")

        for city in self.data["list"]:
            lat, lon = city["coord"]["lat"], city["coord"]["lon"]
            temp = city["main"]["temp"] - 273.15
            humidity = city["main"]["humidity"]
            weather_desc = city["weather"][0]["description"].capitalize()

            popup_html = f"""
            <b>{city['name']}</b><br>
            Temp: {temp:.1f}°C<br>
            Humidity: {humidity}%<br>
            Weather: {weather_desc}
            """
            folium.CircleMarker(
                location=[lat, lon],
                radius=15,
                color="transparent",
                fill=True,
                fill_opacity=0,
                popup=popup_html,
                tooltip=f"Hover for details",
            ).add_to(self.m)
            self.debug(
                f"Added marker for {city['name']} at [{lat}, {lon}] with temp {temp:.1f}°C."
            )

    def create_and_save_map(self, filename="interactive_heatmap.html"):
        """Creates the heatmap and saves it to an HTML file."""
        if not self.m:
            raise ValueError("Map not created. Call create_map() first.")

        folium.LayerControl().add_to(self.m)
        title_html = (
            "<h3 align='center'>West Midlands: Temperature Heatmap + City Data</h3>"
        )
        self.m.get_root().html.add_child(folium.Element(title_html))
        self.debug("Map title and layer control added.")

        self.m.save(filename)
        self.debug(f"Interactive heatmap saved as {filename}")

    def debug(self, message):
        """Debugging method to print messages."""
        if self.debug_enabled:
            pprint(f"[DEBUG] {message}")

    def run(self, filename="interactive_heatmap.html"):
        """Runs the entire process to create and save the interactive heatmap."""
        self.prepare_heatmap()
        self.create_map()
        self.add_heatmap_layer()
        self.add_interactive_markers()
        self.create_and_save_map(filename)
        self.debug("Map creation process completed.")


class WeatherMapApp:
    """Main application class that orchestrates weather data fetching and map creation."""

    def __init__(self, data_file, latitude, longitude, fresh_data=False, debug=False):
        self.data_fetcher = WeatherDataFetcher(
            data_file, latitude, longitude, fresh_data, debug
        )
        self.heatmap = InteractiveHeatmap(self.data_fetcher, debug)

    def create_interactive_heatmap(self, filename="interactive_heatmap.html"):
        """Creates and saves an interactive heatmap."""
        self.heatmap.run(filename)


if __name__ == "__main__":
    file = "weather.json"
    latitude = "52.3886"
    longitude = "-2.2497"
    fresh_data = False
    debug = True

    weather_map = WeatherMapApp(file, latitude, longitude, fresh_data, debug)
    weather_map.create_interactive_heatmap()
