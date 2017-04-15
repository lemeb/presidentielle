import csv, pandas, json
import matplotlib.pyplot as plt
import numpy as np
from lowess import lowess
from scipy.stats import chisquare
from datetime import datetime, timedelta, date

# Importer
sondages = csv.DictReader(open('data/sondages_17.csv'))
sondages_array = []
for sondage in sondages:
	sondages_array.append(sondage)
sondages_df = pandas.DataFrame(sondages_array)

STD_ERROR = 1.35
RED_DATE = date(2017, 4, 23) - timedelta(60,0,0)

CANDIDATES = ['Fillon', 'LePen', 'Melenchon', 'Macron']

PLOT = False

for CANDIDATE in CANDIDATES:
	# Convertir les jours en nombre négatifs
	plot_x = (sondages_df['DayOfSurvey'].values.astype('datetime64'))
	plot_x_numbers = (sondages_df['DaysBefore'].values.astype(int) * -1)
	# Chiffres des sondages
	values_candidate = sondages_df[CANDIDATE].values.astype(float)
	# Moyenne
	movingaverage_candidate = lowess(plot_x_numbers, values_candidate, f=0.3)
	# Deviation from moyenne
	dev_f_moyenne = abs(values_candidate - movingaverage_candidate)
	# Moyenne of deviation from moyenne
	dev_movingaverage = lowess(plot_x_numbers, dev_f_moyenne, f=0.8)


	# Viz
	if PLOT:
		# plt.plot(plot_x, values_candidate, 'k.')
		# plt.plot(plot_x, movingaverage_candidate, 'r')
		plt.plot(plot_x, dev_f_moyenne, 'b.')
		plt.plot(plot_x, dev_movingaverage, 'g')
		# plt.fill_between(plot_x, movingaverage_candidate + STD_ERROR, movingaverage_candidate - STD_ERROR)
		
		# Resultats historiques
		with open('raw/resultats.csv') as resultats_file:
			resultats_reader = csv.DictReader(resultats_file)
			for row in resultats_reader:
				if row['Year'] == '2017' and row['Round'] == '1' and row['Candidate'] == CANDIDATE:
					plt.plot(0, float(row['Result']), 'r.')
		plt.show()

	# Liste de (date, score dans les sondages, moyenne mouvante, date en chiffre)
	in_interval_list = list(zip(plot_x,values_candidate,movingaverage_candidate, plot_x_numbers))
	# Liste de ((Avant le 25 janvier ?), (Dans l'intervalle de la moyenne ?))
	in_interval_list_true_false = list(map(
			lambda args: (True if args[0] < RED_DATE else False, 
							True if abs(
								args[1] - args[2]) < 1.35 else False), in_interval_list))

	TotalBeforeIn, TotalBeforeOut, TotalAfterIn, TotalAfterOut = 0, 0, 0, 0
	for isBefore, isInInterval in in_interval_list_true_false:
		if isBefore == True and isInInterval == True:
			TotalBeforeIn += 1
		if isBefore == True and isInInterval == False:
			TotalBeforeOut += 1
		if isBefore == False and isInInterval == True:
			TotalAfterIn += 1
		if isBefore == False and isInInterval == False:
			TotalAfterOut += 1

	# Pour exporter
	date_and_number = list(map(
			lambda args: {'date':int(args[3] + 160), 'number':float(args[1]), 'average':float(args[2])}, 
			in_interval_list))
	with open('data/'+CANDIDATE+'_graph.json', 'w') as outfile:
		json.dump(date_and_number, outfile)

	print(CANDIDATE, TotalBeforeIn, TotalBeforeOut, TotalAfterIn, TotalAfterOut)
	predictedInBefore = (TotalBeforeIn + TotalBeforeOut) * .68
	predictedOutBefore = (TotalBeforeIn + TotalBeforeOut) * .32
	predictedInAfter = (TotalAfterIn + TotalAfterOut) * .68
	predictedOutAfter = (TotalAfterIn + TotalAfterOut) * .32
	print(chisquare([TotalBeforeIn,TotalBeforeOut],[predictedInBefore, predictedOutBefore]).pvalue)
	print(chisquare([TotalAfterIn,TotalAfterOut],[predictedInAfter, predictedOutAfter]).pvalue)
