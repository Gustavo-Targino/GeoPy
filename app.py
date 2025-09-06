import streamlit as st
import pandas as pd
from db_sqlite import get_sqlite_engine, init_sqlite_db, insert_state, insert_city, get_states, get_cities_by_state
from db_mongo import get_mongo_db, insert_local, get_all_locais, get_locais_by_city_state
from geoprocessamento import haversine_km, locais_no_raio
from utils import states_dict, get_state_symbol_options

st.set_page_config(page_title="Persistência Poliglota Geo", page_icon="🗺️", layout="wide")

st.title("🗺️ Persistência Poliglota: MongoDB + SQLite + Geo (Streamlit)")
st.markdown(
    """
        Esta app demonstra **Persistência Poliglota**: dados tabulares (Estados/Cidades) no **SQLite** e
        **Locais** (documentos JSON com latitude/longitude) no **MongoDB**. Também há funções simples de
        **geoprocessamento** (distância Haversine e busca por raio). O mapa usa `st.map()`.
    """
)

# --- Conexões (cacheadas) ---
@st.cache_resource
def _sqlite_engine():
    eng = get_sqlite_engine()
    init_sqlite_db(eng)
    return eng

@st.cache_resource
def _mongo_db():
    return get_mongo_db()

engine = _sqlite_engine()
mdb = _mongo_db()

# --- Layout em abas ---
tab_cadastro, tab_consulta = st.tabs(["✍️ Cadastro", "🔎 Consultas & Mapa"])

# -----------------------------
#         CADASTRO
# -----------------------------
with tab_cadastro:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("SQLite • Estados e Cidades")

        with st.form("form_estado"):
            st.markdown("**Novo Estado**")
            est_uf = st.selectbox("UF", get_state_symbol_options(), placeholder="Selecione a UF") 
            est_nome = states_dict.get(est_uf, "Nome do Estado")
            
            if st.form_submit_button("Salvar Estado"):
                ok = insert_state(engine, est_nome, est_uf)
                st.success("Estado salvo!" if ok else "Nada inserido (talvez UF já exista ou dados inválidos).")

        with st.form("form_cidade"):
            st.markdown("**Nova Cidade**")
            estados = get_states(engine)
            ufs = [s["uf"] for s in estados]
            sel_uf = st.selectbox("UF do estado", options=ufs) if ufs else st.text_input("UF", max_chars=2)
            cid_nome = st.text_input("Nome da cidade", placeholder="São Paulo")
            if st.form_submit_button("Salvar Cidade"):
                ok = insert_city(engine, cid_nome, sel_uf)
                st.success("Cidade salva!" if ok else "Nada inserido (verifique se o estado existe e se a cidade já não está cadastrada).")

    with col2:
        st.subheader("MongoDB • Locais (Pontos de Interesse)")
        with st.form("form_local"):
            nome_local = st.text_input("Nome do local", placeholder="Praça da Sé")
            cidade = st.text_input("Cidade", placeholder="São Paulo")
            estado = st.text_input("UF do estado", placeholder="SP", max_chars=2)
            lat = st.number_input("Latitude", format="%f")
            lon = st.number_input("Longitude", format="%f")
            descricao = st.text_area("Descrição", placeholder="Ponto turístico central da cidade")
            if st.form_submit_button("Cadastrar Local"):
                _id = insert_local(mdb, nome_local, cidade, estado, lat, lon, descricao)
                if _id:
                    st.success(f"Local cadastrado com sucesso! (id: {_id})")
                else:
                    st.error("Falha ao cadastrar. Verifique os campos e os limites de latitude/longitude.")


# -----------------------------
#       CONSULTAS & MAPA
# -----------------------------
with tab_consulta:
    st.subheader("Integração SQLite ⇄ MongoDB")

    estados = get_states(engine)
    if not estados:
        st.info("Cadastre ao menos um Estado/Cidade na aba **Cadastro** para começar.")
    else:
        colA, colB, colC = st.columns([1, 1, 2])
        sel_estado = colA.selectbox("Estado (UF - Nome)", options=[f"{s['uf']} - {s['name']}" for s in estados])
        sel_uf = sel_estado.split(" - ")[0]
        cidades = get_cities_by_state(engine, sel_uf)
        sel_cidade = colB.selectbox("Cidade", options=cidades) if cidades else colB.text_in