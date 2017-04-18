import csv, pandas, json
import numpy as np

# Importer
sondages = csv.DictReader(open('data/sondages_17.csv'))
sondages_array = []
for sondage in sondages:
	sondages_array.append(sondage)
sondages_df = pandas.DataFrame(sondages_array)

sondages_df_no_jadot_bayrou = sondages_df[
	(sondages_df['Jadot'] == '') & (sondages_df['Bayrou'] == '')]

def empty_to_zero(string):
	return '0' if string == '' else string

sondages_df_no_jadot_bayrou['Cheminade'], sondages_df_no_jadot_bayrou['Asselineau'] = (sondages_df_no_jadot_bayrou['Cheminade'].apply(empty_to_zero),
	sondages_df_no_jadot_bayrou['Asselineau'].apply(empty_to_zero))

candidats = [
	'Arthaud',
	'Poutou',
	'Melenchon',
	'Hamon',
	'Macron',
	'DupontAignan',
	'LePen',
	'Cheminade',
	'Asselineau',
	'Fillon']

def string_to_float(row):
	return row.apply(float)

sondages_df_no_jadot_bayrou['sum'] = sondages_df_no_jadot_bayrou.filter(items=candidats).apply(string_to_float).sum(axis=1)
sondages_df_no_jadot_bayrou[sondages_df_no_jadot_bayrou['sum'] < 100.0].to_csv('data/sondages_not_100.csv')

scores = []
for candidat in candidats:
	scores.append(sondages_df_no_jadot_bayrou[candidat].apply(float))

print(scores)