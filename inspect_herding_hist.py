import csv, pandas, dateparser
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare
from math import ceil
from scipy import linalg
from lowess import lowess

YEAR = '17'
ROUND = 1

sondages = csv.DictReader(open('data/sondages_'+str(YEAR)+'.csv'))
sondages_headers = sondages.fieldnames
sondages_array = []
for sondage in sondages:
	sondages_array.append(sondage)
sondages_df = pandas.DataFrame(sondages_array)

SMOOTHING = 23
STD_ERROR = 1.35

CANDIDATES = ['Fillon2', 'LePen', 'Melenchon', 'Macron']

for CANDIDATE in CANDIDATES:
	plot_x = (sondages_df['DaysBefore'].values.astype(int) * -1)
	values_candidate = sondages_df[CANDIDATE].values.astype(float)
	middle_moving = movingaverage(values_candidate, SMOOTHING)

	yest = lowess(plot_x, values_candidate, f=0.8)

	movingaverage_candidate = yest
	# Old version
	# np.concatenate(
	# 	(np.linspace(
	# 				np.average(values_candidate[:SMOOTHING // 2 - 1]), 
	# 				middle_moving[0], 
	# 				num=(SMOOTHING // 2), endpoint=True),
	# 		middle_moving,
	# 		np.linspace(
	# 			np.average(values_candidate[- 1 * (SMOOTHING // 2 - 1):]), 
	# 			middle_moving[-1], 
	# 			num=(SMOOTHING // 2), endpoint=True))
	# ) 

	plt.plot(plot_x, values_candidate, 'k.')
	plt.plot(plot_x, yest, 'r')
	plt.fill_between(plot_x, yest + STD_ERROR, yest - STD_ERROR)
	# plot(plot_x, moving_average(values_candidate, n=5), 'r')

	with open('raw/resultats.csv') as resultats_file:
		resultats_reader = csv.DictReader(resultats_file)
		for row in resultats_reader:
			if row['Year'] == '20'+str(YEAR) and row['Round'] == '1' and row['Candidate'] == CANDIDATE:
				plt.plot(0, float(row['Result']), 'r.')

	in_interval_list = list(zip(plot_x,values_candidate,movingaverage_candidate))
	in_interval_list = list(map(lambda args: (True if args[0] < -90 else False, True if abs(args[1] - args[2]) < 1.35 else False), in_interval_list))
	TotalBeforeIn = 0
	TotalBeforeOut = 0
	TotalAfterIn = 0
	TotalAfterOut = 0
	for isBefore, isInInterval in in_interval_list:
		if isBefore == True and isInInterval == True:
			TotalBeforeIn += 1
		if isBefore == True and isInInterval == False:
			TotalBeforeOut += 1
		if isBefore == False and isInInterval == True:
			TotalAfterIn += 1
		if isBefore == False and isInInterval == False:
			TotalAfterOut += 1

	print(CANDIDATE, TotalBeforeIn, TotalBeforeOut, TotalAfterIn, TotalAfterOut)
	print(chisquare([TotalBeforeIn,TotalBeforeOut],[42.84, 20.16]).pvalue)
	print(chisquare([TotalAfterIn,TotalAfterOut],[72.08, 33.92]).pvalue)
	plt.show()