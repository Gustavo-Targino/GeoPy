# Persistência Poliglota Geo: SQLite + MongoDB + Geo (Streamlit)

Este projeto demonstra o uso de **persistência poliglota** combinando **SQLite** para dados tabulares (Estados/Cidades) e **MongoDB** para documentos georreferenciados (Locais). Inclui funções de **geoprocessamento** e visualização em mapas interativos com Folium/Google Maps.

## Vídeo de demonstração

[Assista o vídeo no YouTube](https://youtu.be/UrvXInnBxkE)

## Arquitetura Adotada

- **SQLite** (`db_sqlite.py`):
  - Tabelas: `states` e `cities`
  - Operações: Inserção e consulta de estados e cidades
- **MongoDB** (`db_mongo.py`):
  - Coleção: `locais`
  - Documento:
    ```json
    {
      "nome_local": "Praça da Sé",
      "cidade": "São Paulo",
      "estado": "SP",
      "coordenadas": { "latitude": -23.55052, "longitude": -46.633308 },
      "descricao": "Ponto turístico central da cidade"
    }
    ```
  - Operações: Inserção e consulta de locais
- **Geoprocessamento** (`geoprocessamento.py`):
  - Funções:
    - `distancia_km(lat1, lon1, lat2, lon2)`: Distância em linha reta entre dois pontos
    - `locais_no_raio(locais, centro_lat, centro_lon, raio_km)`: Filtra locais dentro de um raio
    - `calcular_distancia_entre_locais(locais)`: Interface Streamlit para calcular distância
    - `buscar_locais_proximos(locais)`: Interface Streamlit para buscar locais próximos
- **Streamlit** (`app.py`):
  - Abas:
    - **Cadastro**: Estados, Cidades (SQLite) e Locais (MongoDB)
    - **Consultas & Mapa**: Consulta de locais, cálculo de distâncias e busca por proximidade
  - Integração com Folium para mapas interativos
  - Camada Google Maps (`utils.google_layer`)

---

## Exemplo de Consultas Realizadas

### 1. Cadastrar Estados e Cidades

```python
insert_state(engine, "São Paulo", "SP")
insert_city(engine, "São Paulo", "SP")
```

### 2. Cadastrar Locais no MongoDB

```python
insert_local(
    db=mdb,
    nome_local="Praça da Sé",
    cidade="São Paulo",
    estado="SP",
    latitude=-23.55052,
    longitude=-46.633308,
    descricao="Ponto turístico central da cidade"
)
```

### 3. Consultar Locais por Cidade e Estado

```python
get_locais_by_city_state(mdb, cidade="São Paulo", estado="SP")
```

### 4. Calcular Distância Entre Dois Locais

```python
distancia_km(-23.55052, -46.633308, -23.561, -46.645)
```

### 5. Buscar Locais Próximos a um Ponto

```python
locais_no_raio(locais, centro_lat=-23.55052, centro_lon=-46.633308, raio_km=5)
```

## Tutorial para Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/Gustavo-Targino/GeoPy.git
cd GeoPy
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
.env
MONGO_URI=mongodb://localhost:27017
```

### 4. Executar a aplicação Streamlit

```bash
streamlit run app.py
```

### 5. Navegar na aplicação

- Aba Cadastro: Inserir Estados, Cidades e Locais

Aba Consultas & Mapa:

- Visualizar todos os locais da cidade

- Calcular distância entre dois locais

- Buscar locais dentro de um raio definido

- Visualizar no mapa interativo com OpenStreetMap ou Google Maps

## Observações

- Garantir que o MongoDB esteja rodando localmente (localhost:27017).
- Distâncias são calculadas em linha reta (geodésica) usando Geopy.
