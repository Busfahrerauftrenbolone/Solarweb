#cd C:\Users\manav\Downloads\Project\Solarweb
import pydeck as pdk
import json
from owslib.wfs import WebFeatureService 
import streamlit as st
import PySimpleGUI as sg
import math
st.set_page_config(layout="wide")

st.title("SOLARWEB ")
# Define the URL of the WFS service 
#https://data.wien.gv.at/daten/geo?version=1.0.0&typeName=ogdwien:FMZKBKMOGD&outputFormat=shape-zip&SRS=EPSG:31256&BBOX=2748,341794,4516,
wfs_url = 'https://data.wien.gv.at/daten/geo?'

# Connect to the WFS service
wfs = WebFeatureService(wfs_url, version='1.1.0')
layer_name = 'ogdwien:SOLARANLAGLSTGOGD'
response = wfs.getfeature(
    typename=layer_name,
    srsname='urn:x-ogc:def:crs:EPSG:31256',
    maxfeatures=10,
    outputFormat="JSON",
    )
json_features = response.read()
feature_collection = json.loads(json_features)
features = feature_collection["features"]
features = [feature for feature in features if feature['properties'].get('STR') != ' ' and feature['properties'].get('ADRESSE') != ' ']
addressbuch = dict()
addressbuch2 = list()

for index, feature in enumerate(features):
    geometry_type = feature['geometry']['type']
    coordinates = feature['geometry']['coordinates']
    properties = feature['properties']
    adresse = feature['properties']['ADRESSE']
    leistung = feature['properties']['YR']
    anlagenleistung = feature['properties']['ANLAGENLEISTUNG']

    if geometry_type == 'Polygon':
        print(f"Adresse: {adresse}")
        print(f"Polygon: Coordinates: {coordinates}")

    addressbuch[index] = {                  # Addressbuch has numerical indices as keys (0, 1, 2, ...)
        "Adresse": adresse,                 # Each index maps to a dictionary containing address information.
        "Leistung": leistung,
        "Anlagenleistung": anlagenleistung
    }

    addressbuch2.append(adresse)




user_address = input("Bitte gib deine Adresse ein (Bezirk., Straße Nr):")
user_address_parts = user_address.split(', ')
user_bezirk, user_strasse_nr = user_address_parts[0], user_address_parts[1]
user_key = f"{user_bezirk}, {user_strasse_nr}"

if user_key in addressbuch2:
    # Get the index for the given user address
    index_for_user_address = addressbuch2.index(user_key)
    print(addressbuch[index_for_user_address])
else:
    print("Address not found. Please try again.")

def dachneigung():
    import PySimpleGUI as sg
    import math

    layout = [
        [sg.Text("Bitte stell deine Dachneigung ein.")],
        [
            sg.Column([
                [sg.Graph(
                    canvas_size=(300, 300),
                    graph_bottom_left=(0, 0),
                    graph_top_right=(300, 300),
                    key="-GRAPH-",
                    background_color="white",
                )]
            ], element_justification='center'),
            sg.Column([
                [
                    sg.Slider(
                        range=(0, 90),
                        default_value=0,
                        orientation="vertical",
                        key="-SLIDER-",
                        enable_events=True,
                    ),
                    sg.Text("0°", key="-DEGREE_TEXT-", size=(10, 1)),
                ]
            ], element_justification='center'),
        ],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window("Dachneigung", layout, finalize=True)

    graph = window["-GRAPH-"]
    slider = window["-SLIDER-"]
    degree_text = window["-DEGREE_TEXT-"]

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'OK':
            rotation_angle = values["-SLIDER-"]
            sg.popup(f'You chose {rotation_angle}°')
            break

        rotation_angle_radians = math.radians(values["-SLIDER-"])  # Convert degrees to radians

        degree_text.update(f"{values['-SLIDER-']}°")

        # Clear the graph
        graph.erase()

        # Draw a horizontal line in black
        horizontal_end_x = 150 + 100
        horizontal_end_y = 150
        graph.draw_line((150, 150), (horizontal_end_x, horizontal_end_y), color="black", width=2)

        # Draw a rotating line in black based on the slider value
        rotated_x = 150 + 100 * math.cos(rotation_angle_radians)
        rotated_y = 150 + 100 * math.sin(rotation_angle_radians)
        graph.draw_line((150, 150), (rotated_x, rotated_y), color="black", width=2)

    window.close()
layout = [
    [sg.Checkbox('Flachdach', key='Flachdach'), sg.Image("Flachdach.png")],
    [sg.Checkbox('Schrägdach', key='Schrägdach'), sg.Image("Schrägdach.png")],
    [sg.Button('OK'), sg.Button('Cancel')]
]

window = sg.Window('Wähle deine Dachform', layout)

event, values = window.read(close=True)

if event == 'OK':
    selected_options = [option for option in ['Flachdach', 'Schrägdach'] if values[option]]
    sg.popup(f'You chose {", ".join(selected_options)}')
    dach_form = selected_options[0] if selected_options else None
    
    if 'Schrägdach' in selected_options:
        dachneigung()

window.close()

index_to_access = index_for_user_address
specific_feature = features[index_to_access]

testadresse = "Wien, " + user_address

from geopy.geocoders import Nominatim

# Replace 'YourAPIKey' with your actual API key if you're using a service that requires one.
geolocator = Nominatim(user_agent="my_geocoder_app")

def get_lat_long_from_address(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Example usage:
address = testadresse
coordinates_adress = get_lat_long_from_address(address)

if coordinates_adress:
    print(f"Latitude: {coordinates_adress[0]}, Longitude: {coordinates_adress[1]}")
else:
    print("Could not retrieve coordinates for the given address.")

from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:31256", "EPSG:4326", always_xy=True)

def transform_coordinates(coords):
    # Assuming coords is a pair of (x, y)
    transformed_coords = [list(transformer.transform(x, y)) for x, y in coords]
    return transformed_coords

def transform_feature(specific_feature):
    coords = specific_feature["geometry"]["coordinates"]
    specific_feature["geometry"]["coordinates"] = [transform_coordinates(coord) for coord in coords]

# Example usage
transform_feature(specific_feature)

from pyproj import Proj, transform
from shapely.geometry import Polygon

def calculate_polygon_area(coordinates):
    # Create a Shapely Polygon from the reprojected coordinates
    polygon = Polygon(coordinates)
    
    # Calculate the area using the Shapely area property
    area = polygon.area
    
    return area

def reproject_coordinates(coordinates, source_crs, target_crs):
    # Create Proj objects for the source and target CRS
    source_proj = Proj(init=source_crs)
    target_proj = Proj(init=target_crs)
    
    # Swap longitude and latitude and reproject each coordinate pair
    reprojected_coordinates = [transform(source_proj, target_proj, y, x) for x, y in coordinates]
    
    return reprojected_coordinates

# Example usage
source_crs = "EPSG:4326"
target_crs = "EPSG:3857"

# Assuming specific_feature is the dictionary you provided
raw_coordinates = specific_feature["geometry"]["coordinates"][0]
reprojected_coordinates = reproject_coordinates(raw_coordinates, source_crs, target_crs)

area = calculate_polygon_area(reprojected_coordinates)
print(f"The area of the polygon is {area} square meters.")

adresse=specific_feature["properties"]["ADRESSE"]
yr=specific_feature["properties"]["YR"]
anlagenleistung=specific_feature["properties"]["ANLAGENLEISTUNG"]
area = round(area,2)
specific_feature.update({"Dachform": dach_form,"Fläche": area,"Adresse":adresse,"YR":yr,"Anlagenleistung": anlagenleistung})


import pydeck as pdk

# Set the initial view state (adjust as needed)
view_state = pdk.ViewState(
    latitude=coordinates_adress[0],
    longitude=coordinates_adress[1],
    zoom=15,
)


# Create a Pydeck layer with a custom tooltip function
layer = pdk.Layer(
    "GeoJsonLayer",
    data=[specific_feature],
    auto_highlight=True,
    pickable=True,
    get_fill_color=[255, 0, specific_feature["properties"]["ANLAGENLEISTUNG"]*255],
    get_line_color=[200, 0, 0],
    get_line_width=10,
)
tooltip = {
    'html': """
        <div>{Adresse}</div>
        <div><b>geschätzte Dachfläche</b></div>
        <div><b>{Fläche} m²</b></div>
        <div><b>Dachform</b></div>
        <div>{Dachform}</div>
        <div><b>PV-Potenzial</b></div>
        <div>{Anlagenleistung} kWp</div>
    """,
    'style': {
        'backgroundColor': 'steelblue',
        'color': 'white'
    }
}


# Create a Pydeck deck
deck = pdk.Deck(
    layer,
    initial_view_state=view_state,
    tooltip = tooltip
)


# Display the Pydeck chart using st.pydeck_chart
st.pydeck_chart(deck)


