"""
StarDash — Load
Insère les 3 tables dans PostgreSQL via psycopg2 + COPY (performant).
"""
import os
import io
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def _copy_df(cursor, df: pd.DataFrame, table: str, columns: list[str]):
    """Insert rapide via COPY FROM STDIN."""
    buffer = io.StringIO()
    df[columns].to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    cursor.copy_expert(
        f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH CSV",
        buffer
    )

def load(tables: dict[str, pd.DataFrame]):
    print("[load] Connexion PostgreSQL...")
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Ordre important : dimensions avant faits (contraintes FK)
        
        print("[load] → dim_machine")
        _copy_df(cur, tables["dim_machine"], "dim_machine",
                 ["machine_id", "product_id", "qualite", "numero_serie"])
        
        print("[load] → dim_temps")
        _copy_df(cur, tables["dim_temps"], "dim_temps",
                 ["temps_id", "timestamp", "heure", "jour_semaine", "semaine"])
        
        print("[load] → fait_capteurs")
        _copy_df(cur, tables["fait_capteurs"], "fait_capteurs", [
            "machine_id", "temps_id", "temp_air", "temp_process", "temp_delta",
            "vitesse_rotation", "couple", "puissance_estimee", "usure_outil",
            "statut_usure", "panne_usure_outil", "panne_dissipation_thermique",
            "panne_surpuissance", "panne_surcharge", "panne_aleatoire", "machine_failure"
        ])
        
        conn.commit()
        
        # Vérification rapide
        for table in ["dim_machine", "dim_temps", "fait_capteurs"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"[load] ✓ {table} : {count} lignes")
        
    except Exception as e:
        conn.rollback()
        print(f"[load] ✗ Erreur : {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    from transform import transform
    tables = transform()
    load(tables)