from typing import List, Dict
from geopy.distance import distance
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import google_layer


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância geodésica entre dois pontos (latitude/longitude) em km usando Geopy.
    """
    return distance((lat1, lon1), (lat2, lon2)).km


def locais_no_raio(locais: List[Dict], centro_lat: float, centro_lon: float, raio_km: float) -> List[Dict]:
    """
    Recebe uma lista de documentos de locais (MongoDB),
    calcula a distância até o ponto informado e retorna apenas os
    que estão dentro do raio (com o campo extra 'distancia_km').
    """
    resultado = []

    for doc in locais:
        try:
            coords = doc.get("coordenadas", {})
            lat = float(coords.get("latitude"))
            lon = float(coords.get("longitude"))
        except (TypeError, ValueError):
            continue

        dist = distancia_km(centro_lat, centro_lon, lat, lon)

        if dist <= raio_km:
            novo = dict(doc)
            novo["distancia_km"] = round(dist, 3)
            resultado.append(novo)

    resultado.sort(key=lambda d: d.get("distancia_km", 999999))
    return resultado


def calcular_distancia_entre_locais(locais: list):
    st.markdown("### Calcular distância entre dois locais")
    locais_nomes = [l["nome_local"] for l in locais]

    local1 = st.selectbox("Local 1", options=locais_nomes, key="local1_calc", index=None, placeholder="Selecione o primeiro local")
    local2 = st.selectbox("Local 2", options=locais_nomes, key="local2_calc", index=None, placeholder="Selecione o segundo local")

    if local1 and local2 and local1 != local2:
        coord1 = next(l["coordenadas"] for l in locais if l["nome_local"] == local1)
        coord2 = next(l["coordenadas"] for l in locais if l["nome_local"] == local2)

        distancia = distancia_km(coord1["latitude"], coord1["longitude"],
                                 coord2["latitude"], coord2["longitude"])
        st.success(f"A distância entre **{local1}** e **{local2}** é de aproximadamente **{distancia:.2f} km (em linha reta)**")
    else:
        st.info("Escolha dois locais diferentes para calcular a distância.")


def buscar_locais_proximos(locais: list):
    st.markdown("### Buscar locais próximos")
    locais_nomes = [l["nome_local"] for l in locais]

    local_ref = st.selectbox("Local de referência", options=locais_nomes, key="local_ref_busca")
    raio_km = st.slider("Raio de busca (km)", min_value=1, max_value=100, value=10, step=1, key="raio_busca_slider")

    if local_ref:
        coord_ref = next(l["coordenadas"] for l in locais if l["nome_local"] == local_ref)

        locais_proximos = locais_no_raio(locais, centro_lat=coord_ref["latitude"],
                                        centro_lon=coord_ref["longitude"], raio_km=raio_km)
        if locais_proximos:
            st.markdown(f"### Locais dentro de {raio_km} km de {local_ref}")
            df_proximos = pd.DataFrame(locais_proximos)
            st.dataframe(df_proximos[["nome_local", "descricao", "distancia_km"]])

            m = folium.Map(location=[coord_ref["latitude"], coord_ref["longitude"]], zoom_start=12)

            google_layer(m)

            folium.Marker(
                location=[coord_ref["latitude"], coord_ref["longitude"]],
                popup=f"{local_ref} (Referência)",
                icon=folium.Icon(color="red", icon="star")
            ).add_to(m)

            for l in locais_proximos:
                if l["nome_local"] != local_ref:
                    folium.Marker(
                        location=[l["coordenadas"]["latitude"], l["coordenadas"]["longitude"]],
                        popup=f"{l['nome_local']} ({l['distancia_km']} km)",
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(m)

            st_folium(m, width=700, height=500)
        else:
            st.warning(f"Não há locais dentro de {raio_km} km de {local_ref}.")
