"""
StarDash — Extract
Télécharge AI4I 2020 depuis UCI et exporte en CSV local.
"""
from ucimlrepo import fetch_ucirepo
from pathlib import Path
import pandas as pd

RAW_PATH = Path(__file__).parent.parent / "data" / "raw_ai4i2020.csv"

def extract() -> pd.DataFrame:
    print("[extract] Téléchargement AI4I 2020 (UCI id=601)...")
    ds = fetch_ucirepo(id=601)
    df = ds.data.features.join(ds.data.targets)
    
    RAW_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(RAW_PATH, index=False)
    print(f"[extract] {len(df)} lignes exportées → {RAW_PATH}")
    return df

if __name__ == "__main__":
    extract()
