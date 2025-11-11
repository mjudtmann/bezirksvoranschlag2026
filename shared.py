from pathlib import Path

import pandas as pd
import geopandas as gpd

BEZIRKE_JSON = 'BEZIRKSGRENZEOGD.json'
BEZIRKE_DATEN = 'Bezirke Daten Voranschlag 2026.csv'

app_dir = Path(__file__).parent
bezirke_daten = pd.read_csv(BEZIRKE_DATEN, sep=';')
print(bezirke_daten)
bezirke_karte = gpd.read_file(BEZIRKE_JSON)
    
df = bezirke_karte.merge(bezirke_daten, how='left',
        left_on='BEZNR', right_on='Bezirk')