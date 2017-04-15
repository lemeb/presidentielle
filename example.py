import json, sys, geoplotlib

from geoplotlib.utils import BoundingBox
from geoplotlib.colors import ColorMap

import json, sys
parrainages_fichier = open('/Users/L/Desktop/Conseil Constitutionnel/parrainagestotal.json', encoding='utf-8')
parrainages_json = json.load(parrainages_fichier, encoding='utf-8')

macron_parrainages = parrainages_json[17]['Parrainages']

departements = {}
for parrainage in macron_parrainages:
	if parrainage["Département"] in departements:
		departements[parrainage["Département"]] += 1
	else:
		departements[parrainage["Département"]] = 1
print(departements)

cmap = ColorMap('Blues', alpha=255, levels=10)

# find the unemployment rate for the selected county, and convert it to color
def get_color(properties):
    key = properties['nom']
    if key in departements:
        color = cmap.to_color(departements[key]/400, .15, 'lin')
        print(departements[key], color)
        return color
    else:
        return [0, 0, 0, 0]


geoplotlib.geojson('departements.geojson.txt', fill=True, color=get_color)
geoplotlib.geojson('departements.geojson.txt', fill=False, color=[255, 255, 255, 64])
geoplotlib.show()