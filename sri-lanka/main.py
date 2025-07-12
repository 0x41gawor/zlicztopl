import json
import folium
from folium import PolyLine
from folium.plugins import PolyLineTextPath

from matplotlib.colors import to_rgba

def hex_to_rgba(hex_color, alpha=0.5):
    rgba = to_rgba(hex_color, alpha)
    return f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3]})'

from folium import MacroElement
from jinja2 import Template

class TooltipStyleFix(MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template(u"""
        {% macro header(this, kwargs) %}
        <style>
            /* Usuń biały box wokół tooltipa */
            .leaflet-tooltip {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
        </style>
        {% endmacro %}
        """)


# Wczytaj dane z pliku JSON (główne punkty)
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Ustawienie początkowego widoku mapy na środek Sri Lanki
sri_lanka_center = [7.8731, 80.7718]
map = folium.Map(location=sri_lanka_center, zoom_start=7)

# Kolory znaczników według kategorii
color_map = {
    "Zabytek": "blue",
    "Safari": "beige",
    "Plaża": "orange",
    "Kultura (show)": "pink",
    "Krajobraz": "darkgreen",
    "Plantacja": "lightgreen",
    "Las deszczowy (UNESCO)": "darkred",
    "Rzeka": "black",
}

# Dodaj znaczniki
for item in data:
    lat = item.get("lat")
    lng = item.get("lng")
    if lat is None or lng is None:
        continue

    popup_html = f"""
    <div style="font-size: 15px;">
        <h3>{item['name']}</h3><br>
        <b>Miasto:</b> {item['city']}<br>
        <b>Typ:</b> {item['category']}<br>
        <b>Czas :</b> {item['time']}<br>
        <b>Opis:</b> {item['info']}<br>
        <a href="{item['google_maps']}" target="_blank">Zobacz w Google Maps</a>
    </div>
    """

    folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color_map.get(item["category"], "blue"), icon="info-sign")
    ).add_to(map)

# 🔽 Wczytaj strzałki z osobnego pliku
with open('arrows.json', 'r', encoding='utf-8') as f:
    arrows = json.load(f)

# 🔁 Dodaj każdą strzałkę jako linię z popupem i tekstowymi strzałkami
# 🔁 Dodaj każdą strzałkę jako linię z tooltipem i tekstowymi strzałkami
for arrow in arrows:
    start_lat, start_lon = arrow["start"]
    end_lat, end_lon = arrow["end"]
    color = arrow.get("color", "#000000")
    tooltip_text = arrow.get("popup", "")  # teraz tooltip na hover

    # Linia
    line = PolyLine(
        locations=[[start_lat, start_lon], [end_lat, end_lon]],
        color=color,
        weight=6
    ).add_to(map)

    # Strzałki wzdłuż linii
    PolyLineTextPath(
        line,
        '     ➤',
        repeat=True,
        offset=7,
        attributes={
            'fill': color,
            'font-weight': 'bold',
            'font-size': '24'
        }
    ).add_to(map)

    # Tooltip na hover
    tooltip_bg_rgba = hex_to_rgba(color, 0.7)

    tooltip_html = folium.Tooltip(
        f'''
        <div style="
            background-color: {tooltip_bg_rgba};
            padding: 4px 8px;
            border-radius: 6px;
            color: black;
            font-size: 14px;
            font-weight: light;
            margin: 6px;
        ">
            {tooltip_text}
        </div>
        ''',
        # <-- bez permanent=True
        direction='top',
        sticky=True
    )

    line.add_child(tooltip_html)

# 🔽 Wczytaj wielokąty z polygons.json
with open('polygons.json', 'r', encoding='utf-8') as f:
    polygons = json.load(f)

# 🔁 Dodaj każdy polygon do mapy
for poly in polygons:
    coords = poly["locations"]
    border_color = poly.get("color", "#000000")
    fill_color = poly.get("fill_color", border_color)
    popup_text = poly.get("popup", "")
    tooltip_text = poly.get("tooltip", "")

    # Popup z dużą czcionką
    popup_html = folium.Popup(
        html=f'<div style="font-size:25px;">{popup_text}</div>',
        max_width=400
    )

    tooltip_bg_rgba = hex_to_rgba(fill_color, 0.9)

    tooltip_style = (
        f'background-color: {tooltip_bg_rgba}; '
        f'padding: 5px 10px; '
        f'border-radius: 8px; '
        f'border: none; '
        f'box-shadow: none; '
        f'color: black; '
        f'font-size: 18px; '
        f'font-weight: bold; '
    )
    tooltip_html = folium.Tooltip(
    f'''
    <div style="
        background-color: {tooltip_bg_rgba};
        padding: 5px 10px;
        border-radius: 8px;
        color: black;
        font-size: 18px;
        font-weight: bold;
        margin: 10px;
    ">
        <h3 style="margin: 0;">{tooltip_text}</h3>
    </div>
    ''',
    permanent=True,
    direction='top',
    sticky=False,
    )

    folium.Polygon(
        locations=coords,
        color=border_color,
        weight=3,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.2,
        tooltip=tooltip_html,
        popup=popup_html
    ).add_to(map)



# Zapisz mapę
map.get_root().add_child(TooltipStyleFix())
map.save("map.html")