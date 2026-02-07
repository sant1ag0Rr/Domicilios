"""
Utilidades compartidas para el proyecto
Funciones comunes para manejo de datos JSON y cálculos
"""

import json
import os
from typing import List, Dict
import math
from datetime import datetime

# Directorio donde se almacenan los archivos JSON
# Usar ruta absoluta basada en la ubicación de este archivo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(file_name: str) -> List[Dict]:
    """
    Carga datos desde un archivo JSON
    
    Args:
        file_name: Nombre del archivo JSON en el directorio data/
        
    Returns:
        Lista de diccionarios con los datos. Lista vacía si el archivo no existe.
    """
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_json(file_name: str, data: List[Dict]):
    """
    Guarda datos en un archivo JSON
    
    Args:
        file_name: Nombre del archivo JSON donde guardar
        data: Lista de diccionarios a guardar
    """
    file_path = os.path.join(DATA_DIR, file_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine
    
    Args:
        lat1: Latitud del primer punto
        lng1: Longitud del primer punto
        lat2: Latitud del segundo punto
        lng2: Longitud del segundo punto
        
    Returns:
        Distancia en kilómetros
    """
    # Radio de la Tierra en kilómetros
    R = 6371
    
    # Convertir diferencias a radianes
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    # Fórmula de Haversine
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * 
         math.cos(math.radians(lat2)) * 
         math.sin(dlng / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_current_timestamp() -> str:
    """
    Retorna el timestamp actual en formato ISO 8601
    
    Returns:
        String con la fecha y hora actual en formato ISO
    """
    return datetime.now().isoformat()


def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Valida que las coordenadas estén dentro de rangos válidos para Medellín
    
    Args:
        lat: Latitud a validar
        lng: Longitud a validar
        
    Returns:
        True si las coordenadas son válidas, False en caso contrario
    """
    # Rangos aproximados para Medellín y área metropolitana
    MEDELLIN_LAT_RANGE = (6.0, 6.5)
    MEDELLIN_LNG_RANGE = (-75.8, -75.4)
    
    return (MEDELLIN_LAT_RANGE[0] <= lat <= MEDELLIN_LAT_RANGE[1] and
            MEDELLIN_LNG_RANGE[0] <= lng <= MEDELLIN_LNG_RANGE[1])
