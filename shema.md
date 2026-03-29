stardash/
├── .venv/                  ← environnement virtuel (gitignore)
├── data/
│   └── raw_ai4i2020.csv    ← données brutes exportées
├── etl/
│   ├── extract.py          ← téléchargement via ucimlrepo
│   ├── transform.py        ← nettoyage, typage, colonnes calculées
│   └── load.py             ← insertion PostgreSQL
├── db/
│   └── init.sql            ← création schéma en étoile
├── dashboard/
│   ├── app.py              ← application Dash principale
│   ├── layouts/            ← onglets / sections
│   └── assets/             ← CSS custom
├── docker-compose.yml      ← services postgres + dashboard
├── Dockerfile              ← image dashboard
├── requirements.txt
├── .env                    ← credentials PostgreSQL (gitignore)
├── .gitignore
└── README.md               ← documentation portfolio