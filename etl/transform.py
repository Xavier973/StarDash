"""
StarDash — Transform
Nettoyage, typage, colonnes calculées, préparation schéma en étoile.
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw_ai4i2020.csv"

# Mapping noms UCI → noms snake_case internes
RENAME_MAP = {
    "Air temperature":      "temp_air",
    "Process temperature":  "temp_process",
    "Rotational speed":     "vitesse_rotation",
    "Torque":               "couple",
    "Tool wear":            "usure_outil",
    "Machine failure":      "machine_failure",
    "TWF":                  "panne_usure_outil",
    "HDF":                  "panne_dissipation_thermique",
    "PWF":                  "panne_surpuissance",
    "OSF":                  "panne_surcharge",
    "RNF":                  "panne_aleatoire",
    "Type":                 "qualite",
}

def _statut_usure(usure: pd.Series) -> pd.Series:
    return pd.cut(
        usure,
        bins=[-1, 99, 199, np.inf],
        labels=["normal", "attention", "critique"]
    ).astype(str)

def transform(df: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    if df is None:
        df = pd.read_csv(RAW_PATH)
    
    print(f"[transform] {len(df)} lignes en entrée")
    
    # --- Renommage ---
    df = df.rename(columns=RENAME_MAP)
    # Product ID est dans l'index ou absent — on le génère
    if "product_id" not in df.columns:
        df["product_id"] = [f"P{i:05d}" for i in range(len(df))]
    
    # --- Colonnes calculées ---
    df["temp_delta"]       = df["temp_process"] - df["temp_air"]
    df["puissance_estimee"] = df["couple"] * df["vitesse_rotation"] * (2 * np.pi / 60)
    df["statut_usure"]     = _statut_usure(df["usure_outil"])
    
    # --- Timestamps simulés (1 mesure / minute depuis t0) ---
    t0 = pd.Timestamp("2024-01-01 06:00:00")
    df["timestamp"] = [t0 + pd.Timedelta(minutes=i) for i in range(len(df))]
    
    # --- Typage booléen ---
    bool_cols = [
        "machine_failure", "panne_usure_outil",
        "panne_dissipation_thermique", "panne_surpuissance",
        "panne_surcharge", "panne_aleatoire"
    ]
    df[bool_cols] = df[bool_cols].astype(bool)
    
    # --- Extraction numéro de série depuis product_id ---
    # product_id format : "M14860" → qualite=M, numero_serie=14860
    df["numero_serie"] = df["product_id"].str[1:]
    
    # =============================================
    # Découpage schéma en étoile
    # =============================================
    
    # dim_machine : 1 ligne par product_id unique
    dim_machine = (
        df[["product_id", "qualite", "numero_serie"]]
        .drop_duplicates(subset=["product_id"])
        .reset_index(drop=True)
    )
    dim_machine.index.name = "machine_id"
    dim_machine = dim_machine.reset_index()
    dim_machine["machine_id"] += 1  # SERIAL commence à 1
    
    # dim_temps : 1 ligne par timestamp (= 1 par mesure ici)
    dim_temps = pd.DataFrame({
        "timestamp":   df["timestamp"],
        "heure":       df["timestamp"].dt.hour,
        "jour_semaine": df["timestamp"].dt.dayofweek,
        "semaine":     df["timestamp"].dt.isocalendar().week.astype(int),
    }).reset_index(drop=True)
    dim_temps.index.name = "temps_id"
    dim_temps = dim_temps.reset_index()
    dim_temps["temps_id"] += 1
    
    # fait_capteurs : jointure pour récupérer les FK
    machine_fk = df[["product_id"]].merge(
        dim_machine[["machine_id", "product_id"]],
        on="product_id"
    )
    
    fait_capteurs = pd.DataFrame({
        "machine_id":                   machine_fk["machine_id"].values,
        "temps_id":                     dim_temps["temps_id"].values,
        "temp_air":                     df["temp_air"].values,
        "temp_process":                 df["temp_process"].values,
        "temp_delta":                   df["temp_delta"].values,
        "vitesse_rotation":             df["vitesse_rotation"].values,
        "couple":                       df["couple"].values,
        "puissance_estimee":            df["puissance_estimee"].values,
        "usure_outil":                  df["usure_outil"].values,
        "statut_usure":                 df["statut_usure"].values,
        "panne_usure_outil":            df["panne_usure_outil"].values,
        "panne_dissipation_thermique":  df["panne_dissipation_thermique"].values,
        "panne_surpuissance":           df["panne_surpuissance"].values,
        "panne_surcharge":              df["panne_surcharge"].values,
        "panne_aleatoire":              df["panne_aleatoire"].values,
        "machine_failure":              df["machine_failure"].values,
    })
    
    print(f"[transform] dim_machine={len(dim_machine)} | dim_temps={len(dim_temps)} | fait_capteurs={len(fait_capteurs)}")
    
    return {
        "dim_machine":  dim_machine,
        "dim_temps":    dim_temps,
        "fait_capteurs": fait_capteurs,
    }

if __name__ == "__main__":
    tables = transform()
    for name, t in tables.items():
        print(f"  {name}: {t.shape} — colonnes: {list(t.columns)}")