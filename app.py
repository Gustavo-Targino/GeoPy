import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from db_sqlite import get_sqlite_engine, init_sqlite_db, insert_state, insert_city, get_states, get_cities_by_state
from db_mongo import get_mongo_db, insert_local, get_all_locais, get_locais_by_city_state
from geoprocessamento import buscar_locais_proximos, calcular_distancia_entre_locais
from utils import select_estado, select_cidade, google_layer

st.set_page_config(page_title="Persistência Poliglota Geo", page_icon="🗺️", layout="wide")

st.title("🗺️ Persistência Poliglota: MongoDB + SQLite + Geo (Streamlit)")
st.markdown(
    """
        Esta app demonstra **Persistência Poliglota**: dados tabulares (Estados/Cidades) no **SQLite** e
        **Locais** (documentos JSON com latitude/longitude) no **MongoDB**. Também há funções simples de
        **geoprocessamento** (distância Haversine e busca por raio). O mapa usa `st.map()`.
    """
)

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

# -----------------------------
#           ABAS
# -----------------------------

tab_home, tab_cadastro, tab_consulta, tab_excluir = st.tabs(["Home🏠", "✍️ Cadastro", "🔎 Consultas & Mapa", "🗑️ Excluir Localização"])

# ---------------------------
#          HOME
# ---------------------------
with tab_home:
    st.title("🌍 Bem-vindo ao GeoPy")
    st.subheader("👥 Integrantes do Grupo")

    st.markdown("""
    - **Gustavo Targino Freire Simão** — RGM: *30283647*
    - **João Vitor Ramos Almeida de Araújo** — RGM: *30081939*
    """)

    st.markdown("""
    ---
    Esta aplicação foi desenvolvida para **gerenciar e visualizar localizações geográficas**.
    Aqui você pode:

    - **Cadastrar Localizações**: inserir um nome, latitude e longitude para salvar pontos no banco de dados.
    - **Calcular Distâncias**: selecionar duas localizações cadastradas e obter a distância entre elas.
    - **Visualizar no Mapa**: os pontos escolhidos são exibidos em um mapa interativo.
    - **Excluir Localizações**: remover pontos específicos ou todos os pontos do banco de dados.
    """)


# -----------------------------
#         CADASTRO
# -----------------------------
with tab_cadastro:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("SQLite • Estados e Cidades")

        with st.form("form_estado", clear_on_submit=True):
            st.markdown("**Novo Estado**")
            est_nome = st.text_input("Nome do estado", placeholder="São Paulo")
            est_uf = st.text_input("UF", placeholder="SP", max_chars=2)
            if st.form_submit_button("Salvar Estado"):
                ok = insert_state(engine, est_nome, est_uf)
                if ok:
                    st.success("Estado salvo!")
                else:
                    st.error("Estado não inserido. Preencha todos os campos ou UF já existe.")

        with st.form("form_cidade", clear_on_submit=True):
            st.markdown("**Nova Cidade**")
            estados = get_states(engine)
            ufs = [s["uf"] for s in estados]
            sel_uf= select_estado(ufs, key="cadastro_uf")
            cid_nome = st.text_input("Nome da cidade", placeholder="São Paulo")
            if st.form_submit_button("Salvar Cidade"):
                ok = insert_city(engine, cid_nome, sel_uf)
                if ok:
                    st.success("Cidade salva!")
                else:
                    st.error("Cidade não inserida. Preencha todos os campos ou cidade já existe.")

    with col2:
        st.subheader("MongoDB • Locais (Pontos de Interesse)")

        estados = get_states(engine)
        ufs = [s["uf"] for s in estados]
        estado = select_estado(ufs, key="local_uf")

        cidades = get_cities_by_state(engine, estado) if estado else []
        cidade = select_cidade(cidades, key="local_cidade")

        with st.form("form_local", clear_on_submit=True):
            nome_local = st.text_input("Nome do local", placeholder="Praça da Sé")
            lat = st.number_input("Latitude (Decimal)", format="%f")
            st.write("Exemplo: -7.14873")
            lon = st.number_input("Longitude (Decimal)", format="%f")
            st.write("Exemplo: -34.79667")
            descricao = st.text_area("Descrição", placeholder="Ponto turístico central da cidade")

            form_desabilitado = not estado or not cidade

            if form_desabilitado:
                st.write("Preencha estado e cidades")

            if st.form_submit_button("Cadastrar Local", disabled=form_desabilitado):
                _id = insert_local(mdb, nome_local, cidade, estado, lat, lon, descricao)
                if _id:
                    st.session_state["last_local_success"] = "Local cadastrado com sucesso!"
                else:
                    st.session_state["last_local_error"] = "Falha ao cadastrar. Verifique os campos e os limites de latitude/longitude."

        if "last_local_success" in st.session_state:
            st.success(st.session_state["last_local_success"])
            
        if "last_local_error" in st.session_state:
            st.error(st.session_state["last_local_error"])
            
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

        sel_estado = colA.selectbox(
            "Estado (UF - Nome)",
            options=[f"{s['uf']} - {s['name']}" for s in estados],
            key="consulta_estado"
        )
        sel_uf = sel_estado.split(" - ")[0]

        cidades = get_cities_by_state(engine, sel_uf)
        sel_cidade = select_cidade(cidades, key="consulta_cidade") if cidades else colB.text_input("Cidade")

        if sel_estado and sel_cidade:
            locais = get_locais_by_city_state(mdb, sel_cidade, sel_uf)

            if locais:
                st.markdown(f"### Locais cadastrados em {sel_cidade} ({sel_uf})")
                df = pd.DataFrame(locais)
                st.dataframe(df[["nome_local", "descricao", "coordenadas"]])

                # Mapa principal
                avg_lat = sum(l["coordenadas"]["latitude"] for l in locais) / len(locais)
                avg_lon = sum(l["coordenadas"]["longitude"] for l in locais) / len(locais)

                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

                google_layer(m)

                for l in locais:
                    folium.Marker(
                        location=[l["coordenadas"]["latitude"], l["coordenadas"]["longitude"]],
                        popup=f"{l['nome_local']}:\n{l['descricao']}",
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(m)
                st_folium(m, width=700, height=500)

                st.divider()

                calcular_distancia_entre_locais(locais)

                st.divider()

                buscar_locais_proximos(locais)
            
            else:
                st.warning(f"Não há locais cadastrados em {sel_cidade} ({sel_uf}).")

# ---------------------------
#        EXCLUIR
# ---------------------------
with tab_excluir:
    st.title("🗑️ Excluir Localização")

    # Buscar locais cadastrados no MongoDB
    locais_existentes = get_all_locais(mdb)
    nomes_locais = [loc["nome_local"] for loc in locais_existentes]

    if not nomes_locais:
        st.warning("Não há localizações para excluir.")
    else:
        # Remover uma localização específica
        st.subheader("Remover uma localização específica")
        local_para_remover = st.selectbox("Escolha a localização para remover", nomes_locais)

        if st.button(f"Remover '{local_para_remover}'", key="remove_specific"):
            mdb["locais"].delete_one({"nome_local": local_para_remover})
            st.success(f"A localização '{local_para_remover}' foi removida com sucesso!")
            st.rerun()

        st.markdown("---")

        # Remover todas as localizações
        if st.button("Remover todas as localizações", key="remove_all"):
            mdb["locais"].delete_many({})
            st.success("Todas as localizações foram removidas com sucesso!")
            st.rerun()
