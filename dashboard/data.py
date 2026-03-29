"""
StarDash — Couche d'accès aux données
Connexion PostgreSQL via SQLAlchemy + requêtes partagées entre layouts.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
from functools import lru_cache

load_dotenv(Path(__file__).parent.parent / ".env")


def get_engine():
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', 5432)}"
        f"/{os.getenv('POSTGRES_DB')}"
    )
    return create_engine(url, pool_pre_ping=True)


_engine = get_engine()


def query(sql: str, params: dict = None) -> pd.DataFrame:
    with _engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ---------------------------------------------------------------------------
# Requêtes partagées (mises en cache au démarrage)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_fait_capteurs() -> pd.DataFrame:
    """Table de faits complète jointe aux dimensions."""
    return query("""
        SELECT
            f.*,
            m.product_id,
            m.qualite,
            m.numero_serie,
            t.timestamp,
            t.heure,
            t.jour_semaine,
            t.semaine
        FROM fait_capteurs f
        JOIN dim_machine m ON f.machine_id = m.machine_id
        JOIN dim_temps   t ON f.temps_id   = t.temps_id
        ORDER BY t.timestamp
    """)


@lru_cache(maxsize=1)
def load_kpis() -> dict:
    """KPIs globaux pour la vue générale."""
    df = load_fait_capteurs()
    total = len(df)
    nb_pannes = df["machine_failure"].sum()
    return {
        "total_cycles":   total,
        "nb_pannes":      int(nb_pannes),
        "taux_panne":     round(nb_pannes / total * 100, 2),
        "taux_dispo":     round((1 - nb_pannes / total) * 100, 2),
    }
