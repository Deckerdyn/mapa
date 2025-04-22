import json
import requests
import itertools
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from shapely.geometry import Point, Polygon
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # Añade esto al inicio

app = FastAPI()

# Configura CORS para permitir conexiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Origen de tu app React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configuración de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

ORS_API_KEY = "5b3ce3597851110001cf62484764e3c552374233ba49e66393fe0bcb"

def get_route(start, end):
    """Obtiene la ruta de OpenRouteService"""
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
    """Carga y procesa las rutas desde el nuevo formato JSON"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
     # Extraer todos los registros de los diferentes conjuntos de datos
    all_records = []
    for dataset in data:
        if "data" in dataset:
            all_records.extend(dataset["data"])
    
    # Ordenar por messageId (con manejo de errores)
    try:
        data_sorted = sorted(
            all_records,
            key=lambda x: int(x.get("messageId", 0))  # Valor por defecto 0 si no existe
        )
    except (ValueError, TypeError) as e:
        print(f"Error al ordenar registros: {e}")
        data_sorted = all_records  # Usar sin ordenar si hay problemas
    
    # Definiciones de rutas (mantener las originales)
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
        try:
            start_item = next(
                item for item in data_sorted 
                if all(item.get("positionStatus", {}).get(k) == v for k, v in rd["start"].items())
            )
            end_item = next(
                item for item in data_sorted 
                if all(item.get("positionStatus", {}).get(k) == v for k, v in rd["end"].items())
            )
            
            if start_item and end_item:
                start_coords = [
                    start_item["positionStatus"]["latitude"],
                    start_item["positionStatus"]["longitude"]
                ]
                end_coords = [
                    end_item["positionStatus"]["latitude"],
                    end_item["positionStatus"]["longitude"]
                ]
                route_coords = get_route(start_coords, end_coords)
                routes[rd["name"]] = route_coords
        except Exception as e:
            print(f"Error procesando ruta {rd['name']}: {e}")
    
    return routes

# Cargar historial de rutas
route_history = load_routes_from_json("combinado.json")

# Generador de coordenadas para simulación
def generate_live_coordinates():
    all_coords = list(itertools.chain(*route_history.values()))
    return itertools.cycle(all_coords)

live_coords_generator = generate_live_coordinates()

# Endpoints de la API
@app.get("/live-route")
async def get_live_route():
    """Endpoint para coordenadas en tiempo real"""
    return JSONResponse({"coords": next(live_coords_generator)})

class Location(BaseModel):
    latitude: float
    longitude: float

@app.get("/history")
async def get_history():
    """Obtener lista de rutas históricas"""
    return JSONResponse({"history": list(route_history.keys())})

@app.get("/track/{route_name}")
async def get_route_by_name(route_name: str):
    """Obtener detalles de una ruta específica"""
    if route_name in route_history:
        return JSONResponse({"route": route_history[route_name]})
    return JSONResponse({"error": "Ruta no encontrada"}, status_code=404)

# Configuración del logger (añade esto al inicio del archivo)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.get("/api/positions")
async def get_positions():
    """Endpoint para obtener todas las posiciones manteniendo la estructura original"""
    try:
        with open("combinado.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # [CORRECCIÓN] Acceder a TODOS los datasets
        main_data = []
        for dataset in data:  # Itera sobre cada objeto del array principal
            if "data" in dataset:
                main_data.extend(dataset["data"])  # Acumula todos los registros
        
        # Limpiar datos innecesarios y mantener estructura compatible
        formatted_data = []
        for item in main_data:
            try:
                formatted_item = {
                    "messageId": item.get("messageId", "N/A"),
                    "positionStatus": item.get("positionStatus", {}),
                    "assetStatus": item.get("assetStatus", {}),
                    "reeferStatus": item.get("reeferStatus", {}),
                    "impactStatus": item.get("impactStatus", {}),
                    "genericSensors": item.get("genericSensors", {})
                }
                
                # Añadir campos calculados
                formatted_item["positionStatus"]["fullAddress"] = (
                    f"{formatted_item['positionStatus'].get('street', '')}, "
                    f"{formatted_item['positionStatus'].get('city', '')}, "
                    f"{formatted_item['positionStatus'].get('state', '')}"
                )
                
                formatted_data.append(formatted_item)
            except Exception as e:
                logger.error(f"Error procesando item: {str(e)}")
                continue

        return JSONResponse({
            "data": sorted(formatted_data, key=lambda x: x["messageId"], reverse=True)
        })
    
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        return JSONResponse(
            {"error": "Error al procesar datos"},
            status_code=500
        )
@app.get("/", response_class=HTMLResponse)
async def serve_map():
    """Servir la interfaz principal"""
    with open("static/html/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())