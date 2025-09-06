import streamlit as st
import folium

def select_estado(ufs: list[str], label: str = "UF do estado", key: str = "estado_select") -> str | None:
    """
    Renderiza um selectbox de UFs. 
    Se não houver estados, exibe desabilitado.
    
    :param ufs: Lista de UFs (strings)
    :param label: Texto do label no select
    :return: A UF selecionada ou None
    """
    possui_estado_cadastro = bool(ufs)
    return st.selectbox(
        "UF do estado",
        options=ufs if possui_estado_cadastro else [],
        index=None,
        placeholder="Selecione um estado" if possui_estado_cadastro else "Cadastre um estado primeiro",
        disabled=not possui_estado_cadastro,
        key=key
    )

def select_cidade(cidades: list[str], label: str = "Cidade", key: str = "cidade_select") -> str | None:
    """
    Renderiza um selectbox de cidades.
    Se não houver cidades, exibe desabilitado.
    
    :param cidades: Lista de nomes de cidades (strings)
    :param label: Texto do label no select
    :return: A cidade selecionada ou None
    """
    possui_cidade_cadastro = bool(cidades)
    return st.selectbox(
        "Cidade",
        options=cidades if possui_cidade_cadastro else [],
        index=None,
        placeholder="Selecione uma cidade" if possui_cidade_cadastro else "Cadastre uma cidade primeiro",
        disabled=not possui_cidade_cadastro,
        key=key
    )

def google_layer(m: folium.Map):
    return folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps',
            overlay=False,
            control=True
        ).add_to(m)