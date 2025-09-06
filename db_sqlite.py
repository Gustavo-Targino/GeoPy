from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import List, Dict, Optional

SQLITE_PATH = "sqlite:///geo_catalog.db"

def get_sqlite_engine() -> Engine:
    return create_engine(SQLITE_PATH, future=True)

def init_sqlite_db(engine: Engine) -> None:
    """Cria tabelas simples de estados e cidades (se não existirem)."""

    ddl_states = text(
        """
        CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                uf TEXT NOT NULL UNIQUE
            );
        """
    )

    ddl_cities = text(
        """
        CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                state_uf TEXT NOT NULL,
            UNIQUE(name, state_uf)
        );
        """
    )

    with engine.begin() as conn:
        conn.execute(ddl_states)
        conn.execute(ddl_cities)

def insert_state(engine: Engine, name: str, uf: str) -> bool:
    if not name or not uf:
        return False
    
    uf = uf.strip().upper()
    sql = text("INSERT OR IGNORE INTO states (name, uf) VALUES (:name, :uf)")
    
    with engine.begin() as conn:
        res = conn.execute(sql, {"name": name.strip(), "uf": uf})
    return res.rowcount > 0

def insert_city(engine: Engine, name: str, state_uf: str) -> bool:
    if not name or not state_uf:
        return False
    
    state_uf = state_uf.strip().upper()
    check = text("SELECT 1 FROM states WHERE uf = :uf")
    ins = text("INSERT OR IGNORE INTO cities (name, state_uf) VALUES (:name, :uf)")
    with engine.begin() as conn:
        exists = conn.execute(check, {"uf": state_uf}).fetchone()
        if not exists:
            return False
        res = conn.execute(ins, {"name": name.strip(), "uf": state_uf})
    return res.rowcount > 0

def get_states(engine):
    sql = text("SELECT uf, name FROM states ORDER BY name")
    with engine.begin() as conn:
        rows = conn.execute(sql).fetchall()
    return [{"uf": r._mapping["uf"], "name": r._mapping["name"]} for r in rows]


def get_cities_by_state(engine, uf: str) -> List[str]:
    sql = text("SELECT name FROM cities WHERE state_uf = :uf ORDER BY name")
    with engine.begin() as conn:
        rows = conn.execute(sql, {"uf": uf.strip().upper()}).fetchall()
    return [r[0] for r in rows]
