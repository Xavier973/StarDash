-- StarDash — Schéma en étoile PostgreSQL
-- À exécuter une fois avant load.py

CREATE TABLE IF NOT EXISTS dim_machine (
    machine_id   SERIAL PRIMARY KEY,
    product_id   VARCHAR(10)  NOT NULL UNIQUE,
    qualite      VARCHAR(1)   NOT NULL CHECK (qualite IN ('L', 'M', 'H')),
    numero_serie VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dim_temps (
    temps_id     SERIAL PRIMARY KEY,
    timestamp    TIMESTAMP    NOT NULL,
    heure        INT          NOT NULL,
    jour_semaine INT          NOT NULL,
    semaine      INT          NOT NULL
);

CREATE TABLE IF NOT EXISTS fait_capteurs (
    id                          SERIAL PRIMARY KEY,
    machine_id                  INT     NOT NULL REFERENCES dim_machine(machine_id),
    temps_id                    INT     NOT NULL REFERENCES dim_temps(temps_id),
    temp_air                    FLOAT   NOT NULL,
    temp_process                FLOAT   NOT NULL,
    temp_delta                  FLOAT   NOT NULL,
    vitesse_rotation            FLOAT   NOT NULL,
    couple                      FLOAT   NOT NULL,
    puissance_estimee           FLOAT   NOT NULL,
    usure_outil                 INT     NOT NULL,
    statut_usure                VARCHAR(20) NOT NULL,
    panne_usure_outil           BOOLEAN NOT NULL DEFAULT FALSE,
    panne_dissipation_thermique BOOLEAN NOT NULL DEFAULT FALSE,
    panne_surpuissance          BOOLEAN NOT NULL DEFAULT FALSE,
    panne_surcharge             BOOLEAN NOT NULL DEFAULT FALSE,
    panne_aleatoire             BOOLEAN NOT NULL DEFAULT FALSE,
    machine_failure             BOOLEAN NOT NULL DEFAULT FALSE
);

-- Index utiles pour les requêtes dashboard
CREATE INDEX IF NOT EXISTS idx_fait_machine  ON fait_capteurs(machine_id);
CREATE INDEX IF NOT EXISTS idx_fait_temps    ON fait_capteurs(temps_id);
CREATE INDEX IF NOT EXISTS idx_fait_failure  ON fait_capteurs(machine_failure);
CREATE INDEX IF NOT EXISTS idx_fait_usure    ON fait_capteurs(statut_usure);