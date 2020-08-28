import json
import requests
import os
from geopy import distance
import folium
from flask import Flask

NEAREST_BARS_AMOUNT = 5

def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lat, lon = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat

def load_file_of_bars(file_name):
    with open(file_name, "r", encoding="CP1251") as my_file:
      file_contents = my_file.read()
    
    loaded_file = json.loads(file_contents)
    
    return loaded_file

def get_coordinates_of_bars(loaded_file):
    coords_bars = []
    for bar in loaded_file:
        bar_info = {
        'title': bar['Name'], 
        'latitude': bar['Latitude_WGS84'],
        'longitude': bar['Longitude_WGS84'],
        'distance': distance.distance((bar['Latitude_WGS84'], bar['Longitude_WGS84']), your_coords).km
        }
        coords_bars.append(bar_info)
    return coords_bars    

def get_distance(coords_bars):
    return coords_bars['distance']

def get_nearest_bars(get_distance, coords_bars):
    nearest_bars = sorted(coords_bars, key=get_distance)[:NEAREST_BARS_AMOUNT]
    return nearest_bars

def create_map_with_bar_labels(your_coords):
    creating_map = folium.Map(location=your_coords)
    
    folium.Marker(
    location=your_coords,
    popup='Вы находитесь здесь',
    icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(creating_map)

    for mark_bar in nearest_bars:
        folium.Marker(
            location=[mark_bar['latitude'], mark_bar['longitude']],
            popup=mark_bar['title'],
            icon=folium.Icon(icon='info-sign')
        ).add_to(creating_map)
    
    creating_map.save('index.html')

def open_map_with_bars():
    with open('index.html') as file:
      return file.read()

if __name__ == "__main__":
    apikey = os.getenv("YANDEX_GEOCODER_API")
    place = input('Где вы находитесь? ')
    your_coords = fetch_coordinates(apikey, place)
    file_name = "Bars.json"
    loaded_file = load_file_of_bars(file_name)
    coords_bars = get_coordinates_of_bars(loaded_file)
    nearest_bars = get_nearest_bars(get_distance, coords_bars)
    map_with_bar_labels = create_map_with_bar_labels(your_coords)
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', open_map_with_bars)
    app.run('0.0.0.0')