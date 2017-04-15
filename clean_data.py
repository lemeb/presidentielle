import csv, pandas 
from datetime import datetime, timedelta
import numpy as np

sondages_raw = csv.DictReader(open('raw/sondages_1.csv'))
sondages_headers = sondages_raw.fieldnames

def all_candidates_present(row):
	if (row['Melenchon'] != '' and row['Macron'] != ''
	    and row['LePen'] != '' and row ['Hamon'] != ''
	    and row['Fillon2'] != ''):
		return True
	return False 

sondages_array = []
for row in sondages_raw:
	if all_candidates_present(row):
		sondages_array.append(row)

sondages_df = pandas.DataFrame(sondages_array).drop('date', axis=1)

def string_to_days_before(string):
	datetime_obj = datetime.strptime(string, '%d/%m/%Y')
	delta = datetime(2017, 4, 23) - datetime_obj
	return delta.days

def string_to_time_object(string):
	return datetime.strptime(string, '%d/%m/%Y')

# Returns an int
def define_time(row):
	if row['DateDeb_Nb'] == row['DateFin_Nb']:
		return row['DateDeb_Nb']
	else:
		if int(row['DateDeb_Nb']) - 1 == int(row['DateFin_Nb']):
			return row['DateFin_Nb']
		else:
			return int(round(np.average([int(row['DateDeb_Nb']), int(row['DateFin_Nb'])])))

# Returns a date object
def day_of_survey(row):
	if row['DateDeb'] == row['DateFin']:
		return row['DateDeb'].date()
	else:
		if row['DateDeb'] - timedelta(1,0,0) == row['DateFin']:
			print('it happens')
			return row['DateFin'].date()
		else:
			diff = row['DateFin'] - row['DateDeb']
			return (row['DateDeb'] + (diff / 2)).date()

# Nettoyage de colonne
sondages_df['DateDeb_Nb'] = sondages_df['DateDeb'].apply(string_to_days_before)
sondages_df['DateDeb'] = sondages_df['DateDeb'].apply(string_to_time_object)
sondages_df['DateFin_Nb'] = sondages_df['DateFin'].apply(string_to_days_before)
sondages_df['DateFin'] = sondages_df['DateFin'].apply(string_to_time_object)
sondages_df['DaysBefore'] = sondages_df.apply(define_time, axis=1)
sondages_df['DayOfSurvey'] = sondages_df.apply(day_of_survey, axis=1)
sondages_df['Fillon'] = sondages_df['Fillon2']

# Nettoyage de table
sondages_df = (sondages_df
				.drop(['Fillon2', 'Duflot', 'Juppe', 'Hollande'], 1)
				.sort('DaysBefore', ascending=False))
print(sondages_df[:5])

sondages_df.to_csv('data/sondages_17.csv', index=False)