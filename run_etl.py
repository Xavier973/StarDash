"""Lance le pipeline ETL complet."""
from etl.extract import extract
from etl.transform import transform
from etl.load import load

if __name__ == "__main__":
    df_raw = extract()
    tables = transform(df_raw)
    load(tables)
    print("\n✅ Pipeline ETL terminé — données prêtes dans PostgreSQL")