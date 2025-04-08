import json
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from shapely.geometry import Point, Polygon
from fastapi.staticfiles import StaticFiles
import itertools  # Agregar al inicio del archivo


app = FastAPI()


# Configurar el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# API Key de OpenRouteService
ORS_API_KEY = "5b3ce3597851110001cf62484764e3c552374233ba49e66393fe0bcb"

def get_route(start, end):
    """
    Consulta OpenRouteService utilizando las coordenadas.
    En la URL se requiere el orden: lng,lat.
    """
    url = (
        f"https://api.openrouteservice.org/v2/directions/driving-car?"
        f"api_key={ORS_API_KEY}&start={start[1]},{start[0]}&end={end[1]},{end[0]}"
    )
    response = requests.get(url)
    data = response.json()
    if "features" in data and data["features"]:
        return data["features"][0]["geometry"]["coordinates"]
    else:
        raise Exception(f"Error en la respuesta de OpenRouteService: {data}")

def load_routes_from_json(file_path: str):
    """
    Carga el JSON, lo ordena y genera los trazados de rutas a partir de definiciones.
    Cada definición tiene un 'name', y criterios para identificar el registro de inicio (start)
    y de fin (end) en el JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Ordenamos por messageId para tener un orden cronológico (opcional)
    data_sorted = sorted(data, key=lambda x: int(x["messageId"]))
    
    # Definiciones de las rutas deseadas.
    # Los criterios (dict) se comparan con los valores en "positionStatus" del JSON.
    route_definitions = [
        
        {
            "name": "RUTA 5, LOS LAGOS - 2 C. LAS HILANDERAS, PUERTO MONTT",
            "start": {"street": "RUTA 5", "state": "LOS LAGOS"},
            "end": {"street": "2 C. LAS HILANDERAS", "city": "PUERTO MONTT"}
        },
        {
            "name": "2 C. LAS HILANDERAS, PUERTO MONTT - RUTA 5, LOS LAGOS",
            "start": {"street": "2 C. LAS HILANDERAS", "city": "PUERTO MONTT"},
            "end": {"street": "RUTA 5", "state": "LOS LAGOS"}
        },
        {
            "name": "RUTA 5, QUELLÓN - ALAMEDA, SANTIAGO",
            "start": {"street": "RUTA 5", "city": "QUELLÓN", "state": "LOS LAGOS"},
            "end": {"street": "ALAMEDA", "city": "SANTIAGO", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "ALAMEDA, SANTIAGO - RUTA 5, QUELLÓN",
            "start": {"street": "ALAMEDA", "city": "SANTIAGO", "state": "REGIÓN METROPOLITANA"},
            "end": {"street": "RUTA 5", "city": "QUELLÓN", "state": "LOS LAGOS"}
        },
        {
            "name": "RUTA 5, LOS LAGOS - RUTA 5, CASA DE LATA",
            "start": {"street": "RUTA 5", "state": "LOS LAGOS"},
            "end": {"street": "RUTA 5", "city": "CASA DE LATA"}
        },
        {
            "name": "RUTA 5, CASA DE LATA - RUTA 5, RIO BUENO",
            "start": {"street": "RUTA 5", "city": "CASA DE LATA"},
            "end": {"street": "RUTA 5", "city": "RIO BUENO"}
        },
        {
            "name": "RUTA 5, RIO BUENO - RUTA 5, LIPINGUE",
            "start": {"street": "RUTA 5", "city": "RIO BUENO"},
            "end": {"street": "RUTA 5", "city": "LIPINGUE"}
        },
        {
            "name": "RUTA 5, LIPINGUE - RUTA 5, LOS GUAPES",
            "start": {"street": "RUTA 5", "city": "LIPINGUE"},
            "end": {"street": "RUTA 5", "city": "LOS GUAPES"}
        },
        {
            "name": "RUTA 5, LOS GUAPES - RUTA 5, ARAUCANÍA",
            "start": {"street": "RUTA 5", "city": "LOS GUAPES"},
            "end": {"street": "RUTA 5", "state": "ARAUCANÍA"}
        },
        {
            "name": "RUTA 5, ARAUCANÍA - S-109, ARAUCANÍA",
            "start": {"street": "RUTA 5", "state": "ARAUCANÍA"},
            "end": {"street": "S-109", "state": "ARAUCANÍA"}
        },
        {
            "name": "S-109, ARAUCANÍA - RUTA 5, BÍO BÍO",
            "start": {"street": "S-109", "state": "ARAUCANÍA"},
            "end": {"street": "RUTA 5", "state": "BÍO BÍO"}
        },
        {
            "name": "RUTA 5, BÍO BÍO - 812 LONGITUDINAL SUR, SECTOR: PERQUILAUQUÉN - RÍO RENAICO",
            "start": {"street": "RUTA 5", "state": "BÍO BÍO"},
            "end": {"street": "812 LONGITUDINAL SUR, SECTOR: PERQUILAUQUÉN - RÍO RENAICO"}
        },
        {
            "name": "812 LONGITUDINAL SUR - RUTA 5, ÑUBLE",
            "start": {"street": "812 LONGITUDINAL SUR, SECTOR: PERQUILAUQUÉN - RÍO RENAICO"},
            "end": {"street": "RUTA 5", "state": "ÑUBLE"}
        },
        {
            "name": "RUTA 5, ÑUBLE - 3425 CARR. PANAMERICANA SUR, MAULE",
            "start": {"street": "RUTA 5", "state": "ÑUBLE"},
            "end": {"street": "3425 CARR. PANAMERICANA SUR", "state": "MAULE"}
        },
        {
            "name": "3425 CARR. PANAMERICANA SUR - RUTA 5, MAULE",
            "start": {"street": "3425 CARR. PANAMERICANA SUR", "state": "MAULE"},
            "end": {"street": "RUTA 5", "state": "MAULE"}
        },
        {
            "name": "RUTA 5, MAULE - 256 LONGITUDINAL SUR, SECTOR: PEOR ES NADA - PERQUILAUQUÉN",
            "start": {"street": "RUTA 5", "state": "MAULE"},
            "end": {"street": "256 LONGITUDINAL SUR, SECTOR: PEOR ES NADA - PERQUILAUQUÉN"}
        },
        {
            "name": "256 LONGITUDINAL SUR - RUTA 5, O'HIGGINS",
            "start": {"street": "256 LONGITUDINAL SUR, SECTOR: PEOR ES NADA - PERQUILAUQUÉN"},
            "end": {"street": "RUTA 5", "state": "O'HIGGINS"}
        },
        {
            "name": "RUTA 5, O'HIGGINS - SANTIAGO, REGIÓN METROPOLITANA",
            "start": {"street": "RUTA 5", "state": "O'HIGGINS"},
            "end": {"street": "RUTA 5", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "SANTIAGO - 6 SAN JOSÉ DE NOS, SAN BERNARDO",
            "start": {"street": "RUTA 5", "state": "REGIÓN METROPOLITANA"},
            "end": {"street": "6 SAN JOSÉ DE NOS", "city": "SAN BERNARDO"}
        },
        {
            "name": "6 SAN JOSÉ DE NOS - AV. CALERA DE TANGO, CALERA DE TANGO",
            "start": {"street": "6 SAN JOSÉ DE NOS", "city": "SAN BERNARDO"},
            "end": {"street": "AV. CALERA DE TANGO", "city": "CALERA DE TANGO"}
        },
        {
            "name": "AV. CALERA DE TANGO - 1 LOS TILOS, REGIÓN METROPOLITANA",
            "start": {"street": "AV. CALERA DE TANGO", "city": "CALERA DE TANGO"},
            "end": {"street": "1 LOS TILOS", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "1 LOS TILOS - AV. BERLÍN, REGIÓN METROPOLITANA",
            "start": {"street": "1 LOS TILOS", "state": "REGIÓN METROPOLITANA"},
            "end": {"street": "AV. BERLÍN", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "AV. BERLÍN - AV. VICUÑA MACKENNA, PENAFLOR",
            "start": {"street": "AV. BERLÍN", "state": "REGIÓN METROPOLITANA"},
            "end": {"street": "AV. VICUÑA MACKENNA", "city": "PENAFLOR"}
        },
        {
            "name": "AV. VICUÑA MACKENNA - PDTE. JORGE ALESSANDRI, MAIPO",
            "start": {"street": "AV. VICUÑA MACKENNA", "city": "PENAFLOR"},
            "end": {"street": "PDTE. JORGE ALESSANDRI", "state": "MAIPO"}
        },
        {
            "name": "PDTE. JORGE ALESSANDRI - PADRE ALBERTO HURTADO, SANTIAGO",
            "start": {"street": "PDTE. JORGE ALESSANDRI", "state": "MAIPO"},
            "end": {"street": "PADRE ALBERTO HURTADO", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "RUTA 5, LOS LAGOS - 2 C. LAS HILANDERAS, PUERTO MONTT",
            "start": {"street": "RUTA 5", "state": "LOS LAGOS"},
            "end": {"street": "2 C. LAS HILANDERAS", "city": "PUERTO MONTT"}
        },
        {
            "name": "2 C. LAS HILANDERAS, PUERTO MONTT - AV. VICUÑA MACKENNA",
            "start": {"street": "2 C. LAS HILANDERAS", "city": "PUERTO MONTT"},
            "end": {"street": "AV. VICUÑA MACKENNA", "state": "REGIÓN METROPOLITANA"}
        },
        {
            "name": "PUNTO INTERMEDIO, LOS LAGOS - RUTA 5, LOS LAGOS",
            "start": {"street": "PUNTO INTERMEDIO", "state": "LOS LAGOS"},
            "end": {"street": "RUTA 5", "state": "LOS LAGOS"}
        },
        
        # {
        #     "name": "RUTA 5, LOS LAGOS - ANCUD, CHILOÉ",
        #     "start": {"street": "RUTA 5", "state": "LOS LAGOS"},
        #     "end": {"street": "ANCUD", "city": "CHILOÉ"}
        # }
    ]
    
    routes = {}
    for rd in route_definitions:
        # Buscar en el JSON el primer registro que cumpla el criterio de inicio...
        start_item = next(
            (item for item in data_sorted 
             if all(item["positionStatus"].get(k) == v for k, v in rd["start"].items())),
            None
        )
        # ...y el primer registro que cumpla el criterio de fin
        end_item = next(
            (item for item in data_sorted 
             if all(item["positionStatus"].get(k) == v for k, v in rd["end"].items())),
            None
        )
        if start_item and end_item:
            # Extraemos las coordenadas: [latitude, longitude]
            start_coords = [
                start_item["positionStatus"]["latitude"],
                start_item["positionStatus"]["longitude"]
            ]
            end_coords = [
                end_item["positionStatus"]["latitude"],
                end_item["positionStatus"]["longitude"]
            ]
            try:
                # Consultamos ORS para obtener el trazado de la ruta
                route_coords = get_route(start_coords, end_coords)
                routes[rd["name"]] = route_coords
            except Exception as e:
                print(f"Error generando la ruta {rd['name']}: {e}")
        else:
            print(f"Advertencia: No se encontró registro para la ruta {rd['name']}")
    return routes

# Se generan los trazados de las rutas a partir del JSON
route_history = load_routes_from_json("12.02.25.json")

# Generador cíclico de coordenadas de todas las rutas (para simulación)
def generate_live_coordinates():
    all_coords = list(itertools.chain(*route_history.values()))  # Todas las coordenadas
    return itertools.cycle(all_coords)  # Crea un ciclo infinito

live_coords_generator = generate_live_coordinates()

@app.get("/live-route")
async def get_live_route():
    return JSONResponse({"coords": next(live_coords_generator)})

class Location(BaseModel):
    latitude: float
    longitude: float









# Endpoint que retorna el historial de rutas (lista de nombres)
@app.get("/history")
async def get_history():
    return JSONResponse({"history": list(route_history.keys())})

# Endpoint que retorna el trazado de una ruta específica
@app.get("/track/{route_name}")
async def get_route_by_name(route_name: str):
    if route_name in route_history:
        return JSONResponse({"route": route_history[route_name]})
    else:
        return JSONResponse({"error": "Ruta no encontrada"}, status_code=404)
# Endpoint para obtener datos crudos del JSON
@app.get("/api/positions")
async def get_positions():
    with open("12.02.25.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    data_sorted = sorted(data, key=lambda x: int(x["messageId"]))
    return JSONResponse(data_sorted)

# Servidor HTML con el mapa y animación del camión
@app.get("/", response_class=HTMLResponse)
async def serve_map():
    tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Historial de Rutas - Animación del Camión</title>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            box-sizing: border-box;
        }}

        #app-header {{
            background: #007bff;
            color: white;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 60px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-sizing: border-box;
        }}

        body {{
            display: flex;
            font-family: Arial, sans-serif;
            flex-wrap: nowrap;
            background: #f0f2f5;
            padding-top: 60px;
            box-sizing: border-box;
        }}

        #history {{
            flex: 0 0 25%;
            height: 100%;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            min-width: 300px;
            z-index: 2;
        }}

        #map {{
            flex: 1;
            height: 100%;
            min-width: 50%;
            z-index: 1;
            transition: all 0.3s;
        }}

        #info-panel {{
            flex: 0 0 25%;
            height: 100%;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
            box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            min-width: 300px;
            z-index: 2;
        }}

        /* Resto de estilos (ajustados con doble llave) */
        #header-title {{
            margin: 0;
            font-size: 1.5rem;
            padding-left: 20px;
        }}

        #header-controls {{
            display: flex;
            gap: 15px;
            padding-right: 20px;
        }}

        .header-button {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 4px;
            padding: 8px 15px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .header-button:hover {{
            background: rgba(255,255,255,0.2);
        }}
        body {{
            display: flex;
            font-family: Arial, sans-serif;
            flex-wrap: nowrap;
            background: #f0f2f5;
        }}
        #history {{
            flex: 0 0 25%;
            height: 100vh;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            min-width: 300px;
            z-index: 2;
        }}
        #map {{
            flex: 1;
            height: 100vh;
            min-width: 50%;
            z-index: 1;
            transition: all 0.3s;
        }}
        #info-panel {{
            flex: 0 0 25%;
            height: 100vh;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
            box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            min-width: 300px;
            z-index: 2;
        }}
        button {{
            display: block;
            width: 100%;
            margin: 8px 0;
            padding: 12px;
            border: none;
            background: #007bff;
            color: white;
            cursor: pointer;
            font-size: 14px;
            border-radius: 6px;
            transition: all 0.3s;
            text-align: left;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        #live-toggle {{
            background: #28a745;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
        }}
        #live-toggle:hover {{
            background: #218838;
        }}
        .info-item {{
            padding: 15px;
            margin: 10px 0;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s;
            border-left: 4px solid #007bff;
        }}
        .info-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }}
        h2 {{
            color: #2c3e50;
            margin: 0 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 2px solid #eeeeee;
            font-size: 1.4em;
        }}
        .leaflet-container {{
            background: #f8f9fa !important;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        #history-list button {{
            animation: fadeIn 0.5s ease-out;
        }}
        #history-search, #info-search {{
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        </style>
    </head>
    <body>
     <header id="app-header">
            <h1 id="header-title">Monitor de Rutas Logísticas</h1>
            <div id="header-controls">
                <button class="header-button" onclick="toggleLiveMode()">⏯️ Simulación</button>
                <!-- <button class="header-button" onclick="loadInfoData()">🔄 Actualizar Datos</button> -->
            </div>
        </header>
        <div id="history">
            <!-- <h2>Controles</h2>
            <button id="live-toggle" onclick="toggleLiveMode()">Iniciar Simulación en Vivo</button> -->
            <h2>Historial</h2>
            <input type="text" id="history-search" placeholder="Buscar">
            <div id="history-list"></div>
        </div>
        <div id="map"></div>
        <div id="info-panel">
            <h2>Localizaciones</h2>
            <input type="text" id="info-search" placeholder="Buscar por ID, calle, ciudad o estado">
            <div id="info-content"></div>
        </div>

        <script>
    var map = L.map('map').setView([-41.4682, -72.9441], 10);
    L.tileLayer('{tile_url}', {{
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }}).addTo(map);

    var truckIcon = L.icon({{
        iconUrl: '/static/camion.png',
        iconSize: [40, 40],
        iconAnchor: [20, 40]
    }});
    var truckMarker = L.marker([-41.4682, -72.9441], {{ icon: truckIcon }}).addTo(map);
    
    var routeLine = L.polyline([], {{ color: 'blue' }}).addTo(map);
    var animationInterval = null;
    var liveMode = false;
    var liveInterval = null;

    var puertoMonttCoords = [
        [-73.20, -41.43],
        [-72.90, -41.43],
        [-72.90, -41.55],
        [-73.20, -41.55],
        [-73.20, -41.43]
    ];

    var puertoMonttPolygon = L.polygon(
        puertoMonttCoords.map(coord => [coord[1], coord[0]]),
        {{ color: 'red', fillOpacity: 0.1 }}
    ).addTo(map);

    function isPointInPolygon(lat, lng, polygon) {{
        var x = lng, y = lat;
        var inside = false;
        for (var i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {{
            var xi = polygon[i][0], yi = polygon[i][1];
            var xj = polygon[j][0], yj = polygon[j][1];
            var intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }}
        return inside;
    }}

    var wasInsidePuertoMontt = true;

    function updateLivePosition() {{
        fetch('/live-route')
            .then(response => response.json())
            .then(data => {{
                let newLatLng = [data.coords[1], data.coords[0]];
                truckMarker.setLatLng(newLatLng);
                map.panTo(newLatLng, {{ animate: true, duration: 0.5 }});
                var currentLat = newLatLng[0];
                var currentLng = newLatLng[1];
                var isInside = isPointInPolygon(currentLat, currentLng, puertoMonttCoords);
                if (wasInsidePuertoMontt && !isInside) {{
                    alert('¡El camión ha salido de Puerto Montt!');
                }}
                wasInsidePuertoMontt = isInside;
            }});
    }}

    function toggleLiveMode() {{
        liveMode = !liveMode;
        const btn = document.getElementById('live-toggle');
        btn.textContent = liveMode ? 'Detener Simulación' : 'Iniciar Simulación en Vivo';
        if (liveMode) {{
            liveInterval = setInterval(updateLivePosition, 2000);
        }} else {{
            clearInterval(liveInterval);
        }}
    }}

    var fullHistory = [];
    var fullPositions = [];

    function displayHistory(historyArray) {{
        var historyDiv = document.getElementById('history-list');
        historyDiv.innerHTML = "";
        historyArray.forEach(name => {{
            var btn = document.createElement('button');
            btn.innerText = name;
            btn.onclick = function() {{ viewRoute(name); }};
            historyDiv.appendChild(btn);
        }});
    }}

    function loadHistory() {{
        fetch('/history')
            .then(response => response.json())
            .then(data => {{
                fullHistory = data.history;
                displayHistory(fullHistory);
            }});
    }}

    document.getElementById('history-search').addEventListener('input', function() {{
        var term = this.value.trim().toLowerCase();
        if (term === "") {{
            displayHistory(fullHistory);
        }} else {{
            var filtered = fullHistory.filter(function(name) {{
                return name.toLowerCase().includes(term);
            }});
            displayHistory(filtered);
        }}
    }});

    function viewRoute(routeName) {{
        fetch('/track/' + encodeURIComponent(routeName))
            .then(response => response.json())
            .then(data => {{
                let coordinates = data.route;
                if (animationInterval) clearInterval(animationInterval);
                if (routeLine) map.removeLayer(routeLine);
                routeLine = L.polyline([], {{ color: 'blue' }}).addTo(map);
                truckMarker.setLatLng([coordinates[0][1], coordinates[0][0]]);
                let index = 0;
                animationInterval = setInterval(() => {{
                    if (index < coordinates.length) {{
                        let newLatLng = [coordinates[index][1], coordinates[index][0]];
                        truckMarker.setLatLng(newLatLng);
                        routeLine.addLatLng(newLatLng);
                        map.panTo(newLatLng, {{ animate: true, duration: 0.5 }});
                        index++;
                    }} else {{
                        clearInterval(animationInterval);
                    }}
                }}, 10);
            }});
    }}

    function displayInfo(positionsArray) {{
        const infoContent = document.getElementById('info-content');
        infoContent.innerHTML = positionsArray.map(item => `
            <div class="info-item" onclick="focusOnPosition(${{item.positionStatus.latitude}}, ${{item.positionStatus.longitude}})">
                <strong>ID:</strong> ${{item.messageId}}<br>
                <strong>Calle:</strong> ${{item.positionStatus.street}}<br>
                <strong>Ciudad:</strong> ${{item.positionStatus.city || 'N/A'}}<br>
                <strong>Estado:</strong> ${{item.positionStatus.state}}
            </div>
        `).join('');
    }}

    function loadInfoData() {{
        fetch('/api/positions')
            .then(response => response.json())
            .then(data => {{
                fullPositions = data;
                displayInfo(fullPositions);
            }});
    }}

    document.getElementById('info-search').addEventListener('input', function() {{
        var term = this.value.trim().toLowerCase();
        var filtered = fullPositions.filter(item => {{
            return item.messageId.toLowerCase().includes(term) ||
                   (item.positionStatus.street || '').toLowerCase().includes(term) ||
                   (item.positionStatus.city || '').toLowerCase().includes(term) ||
                   (item.positionStatus.state || '').toLowerCase().includes(term);
        }});
        displayInfo(filtered);
    }});

    function focusOnPosition(lat, lng) {{
        map.setView([lat, lng], 15);
        truckMarker.setLatLng([lat, lng]);
    }}

    loadHistory();
    loadInfoData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
