import urllib.request
import json
from flask import Flask, render_template
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def fetch_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    response = urllib.request.urlopen(url)
    if response.getcode() == 200:
        data = response.read()
        earthquake_data = json.loads(data)
        # Save data to a JSON file in Replit
        with open("earthquake_data.json", "w") as json_file:
            json.dump(earthquake_data, json_file)
        print("Data fetched and saved successfully.")
    else:
        print(f"Failed to retrieve data, response code: {response.getcode()}")
app = Flask(__name__)

@app.route("/")
def earthquake_map():
    # Load earthquake data from the JSON file
    with open("earthquake_data.json", "r") as json_file:
        data = json.load(json_file)

    # Extract relevant data into a DataFrame
    records = []
    tsunami_places = set()
    for feature in data["features"]:
        place = feature["properties"]["place"]
        magnitude = feature["properties"]["mag"]
        tsunami = feature["properties"].get("tsunami", 0)
        latitude = feature["geometry"]["coordinates"][1]
        longitude = feature["geometry"]["coordinates"][0]
        records.append({"place": place, "magnitude": magnitude, "latitude": latitude, "longitude": longitude, "tsunami": tsunami})
        if tsunami == 1:
            tsunami_places.add(place)

    df = pd.DataFrame(records)

    # Create a map with markers clustered
    m = folium.Map(location=[20, 0], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"<b>{row['place']}</b><br>Magnitude: {row['magnitude']}",
            icon=folium.Icon(color="red" if row["magnitude"] >= 5 else "blue"),
        ).add_to(marker_cluster)

    # Generate bar chart using Plotly
    bar_chart = px.bar(
        df.groupby("place").mean().reset_index(),
        x="place",
        y="magnitude",
        title="Average Magnitude by Location",
        labels={"magnitude": "Average Magnitude", "place": "Location"},
    )
    bar_chart.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    bar_chart_html = bar_chart.to_html(full_html=False)

    # Dynamically generate tsunami risk list
    tsunami_list = sorted(tsunami_places)

    # Render the map to HTML
    map_html = m._repr_html_()
    return render_template("map.html", map_html=map_html, bar_chart_html=bar_chart_html, tsunami_list=tsunami_list)

if __name__ == "__main__":
    fetch_earthquake_data()
    app.run(host="0.0.0.0", port=5500)