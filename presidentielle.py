import csv, pandas 
from datetime import datetime
import numpy as np

sondages = csv.DictReader(open('data/socp.csv'))
sondages_headers = sondages.fieldnames
sondages_array = []

for sondage in sondages:
	sondages_array.append(sondage)
sondages_df = pandas.DataFrame(sondages_array).drop('date', axis=1)

def string_to_days_before(string):
	datetime_obj = datetime.strptime(string, '%d/%m/%Y')
	delta = datetime(2017, 5, 23) - datetime_obj
	return delta.days

def define_time(row):
	if row['DateDeb'] == row['DateFin']:
		return row['DateDeb']
	else:
		if int(row['DateDeb']) - 1 == int(row['DateFin']):
			return row['DateFin']
		else:
			return int(round(np.average([int(row['DateDeb']), int(row['DateFin'])])))

sondages_df['DateDeb'] = sondages_df['DateDeb'].apply(string_to_days_before)
sondages_df['DateFin'] = sondages_df['DateFin'].apply(string_to_days_before)
sondages_df['DaysBefore'] = sondages_df.apply(define_time, axis=1)
sondages_df = sondages_df.sort('DaysBefore', ascending=False)
print(sondages_df[:5])

sondages_df.to_csv('data/sondages_17.csv', index=False)