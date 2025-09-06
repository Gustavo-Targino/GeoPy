from math import radians, sin, cos, asin, sqrt
from typing import List, Dict


# Distância entre dois pontos (latitude/longitude) em quilômetros
# Fórmula de Haversine
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # raio médio da Terra em km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def locais_no_raio(locais: List[Dict], centro_lat: float, centro_lon: float, raio_km: float) -> List[Dict]:
    """Recebe uma lista de documentos de locais (MongoDB),
    calcula a distância até o ponto informado e retorna apenas os
    que estão dentro do raio (com o campo extra 'distance_km')."""

    resultado = []
    for doc in locais:
        try:
            coords = doc.get("coordenadas", {})
            lat = float(coords.get("latitude"))
            lon = float(coords.get("longitude"))
        except (TypeError, ValueError):
            continue

    dist = haversine_km(centro_lat, centro_lon, lat, lon)

    if dist <= raio_km:
        novo = dict(doc)
        novo["distance_km"] = round(dist, 3)
        resultado.append(novo)

    resultado.sort(key=lambda d: d.get("distance_km", 999999))
    return resultado