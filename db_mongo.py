import os
from typing import List, Dict, Optional
from pymongo import MongoClient
from dotenv import load_dotenv


# Estrutura do documento:
#   {
#       "nome_local": str,
#       "cidade": str,
#       "estado": str, # UF (ex.: "SP")
#       "coordenadas": {"latitude": float, "longitude": float},
#       "descricao": str
#   }


_DB_NAME = "persistencia_geo"
_COLLECTION = "locais"

def get_mongo_db():
    load_dotenv()
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    return client[_DB_NAME]

def insert_local(db, nome_local: str, cidade: str, estado: str, latitude: float, longitude: float, descricao: str = "") -> Optional[str]:
    try:
        lat = float(latitude)
        lon = float(longitude)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
    except (TypeError, ValueError):
        return None

    doc = {
        "nome_local": (nome_local or "").strip(),
        "cidade": (cidade or "").strip(),
        "estado": (estado or "").strip().upper(),
        "coordenadas": {"latitude": lat, "longitude": lon},
        "descricao": (descricao or "").strip(),
    }

    if not doc["nome_local"] or not doc["cidade"] or not doc["estado"]:
        return None

    res = db[_COLLECTION].insert_one(doc)
    return str(res.inserted_id)

def get_all_locais(db) -> List[Dict]:
    return list(db[_COLLECTION].find({}, {"_id": 0}))

def get_locais_by_city_state(db, cidade: str, estado: str) -> List[Dict]:
    q = {
        "cidade": {"$regex": f"^{cidade}$", "$options": "i"},
        "estado": estado.strip().upper(),
    }
    
    return list(db[_COLLECTION].find(q, {"_id": 0}))