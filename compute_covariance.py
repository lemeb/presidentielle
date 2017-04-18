import csv, pandas, json, random
import numpy as np
from scipy.stats import pearsonr, norm
from itertools import combinations, combinations_with_replacement

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
	'Fillon',
	'Lassalle']

# Importer
sondages = csv.DictReader(open('data/sondages_17.csv'))
sondages_array = []
for sondage in sondages:
	sondages_array.append(sondage)
sondages_df = pandas.DataFrame(sondages_array[:-2])

# Clean 
def empty_to_zero(string):
	return '0' if string == '' else string
def string_to_float_and_empty_to_zero(row):
	return row.apply(empty_to_zero).apply(float)

sondages_df[candidats] = sondages_df[candidats].apply(string_to_float_and_empty_to_zero, axis=1)
sondages_df['DaysBefore'] = sondages_df['DaysBefore'].apply(int)
df_clean = sondages_df[
	(sondages_df['Jadot'] == '') & (sondages_df['Bayrou'] == '')]

# Normalize
df_clean['sum'] = df_clean.filter(items=candidats).sum(axis=1)
def normalize(row, total=100):
	r_sum = row['sum']
	return row[candidats].apply(lambda value: value * (total/r_sum))
df_clean[candidats] = normalize(df_clean)


## WEIGHTED AVERAGE


# Weight by time
HALF_LIFE_FACTOR = 3
HALF_LIFE_DURATION = 10
last_survey_day = pandas.DataFrame.min(df_clean['DaysBefore'])
def half_lifing(days_before):
	return 1 / (HALF_LIFE_FACTOR ** ((days_before - last_survey_day) / HALF_LIFE_DURATION))

half_life_survey = df_clean['DaysBefore'].apply(half_lifing)
df_clean['WeightTime'] = half_life_survey

# Penaliser les sondages d'un même institut
all_instituts = set(df_clean['Institut'])
df_clean['SameInstituteWeight'] = np.ones(len(df_clean))
HALF_LIFE_PENALTY = 3
for institut in all_instituts:
	def ins_weight(list_candidates):
		length = len(list_candidates)
		list_candidates = list_candidates * (list(reversed(range(0,length))))
		list_candidates = list_candidates.apply(
			lambda val: 1 / (HALF_LIFE_PENALTY ** val))
		return list_candidates

	df_clean.loc[df_clean['Institut'] == institut, 'SameInstituteWeight'] = (
		ins_weight(df_clean[df_clean['Institut'] == institut]['SameInstituteWeight']))

# Take sample size into account
FACTOR_SAMPLESIZE = 0.4
mediane_sondages = np.median(df_clean['N'].apply(int))
weight_sample_survey = df_clean['N'].apply(int).apply(
	lambda size: (size / mediane_sondages) ** FACTOR_SAMPLESIZE)
df_clean['WeightSize'] = weight_sample_survey
df_clean['CombinedWeight'] = df_clean['WeightSize'] * df_clean['WeightTime'] * df_clean['SameInstituteWeight']

def apply_weighted_average(row):
	return (row[:-1].apply(lambda val: val * row['CombinedWeight']))
weighted_average = df_clean[candidats + ['CombinedWeight']].apply(apply_weighted_average, axis=1).sum(axis=0)
total_weights = df_clean['CombinedWeight'].sum()
wa_matrix = weighted_average / total_weights


## CORRELATION MATRIX


# Correlation matrix w/ pvalue
corr_matrix_with_pvalue = pandas.DataFrame(index=candidats, columns=candidats)
for candidat1, candidat2 in list(combinations_with_replacement(candidats, 2)):
	corr_pvalue = pearsonr(df_clean[candidat1], df_clean[candidat2])
	corr_matrix_with_pvalue[candidat1][candidat2] = corr_pvalue
	corr_matrix_with_pvalue[candidat2][candidat1] = corr_pvalue

# Correlation matrix 
corr_matrix = df_clean[candidats].corr()

## SIMULATION

z_critical = norm.ppf(q = 1-(1-0.95)/2)
def get_deviation(score, mediane):
	return z_critical * np.sqrt((score*(100-score))/mediane)
print(get_deviation(50, 1500), get_deviation(20,1000))

for candidate in wa_matrix.index.values:
	candidate_array = []
	mu = wa_matrix[candidate]
	sigma = get_deviation(wa_matrix[candidate], mediane_sondages)
	for i in range(10000):
		simulated = random.gauss(mu, sigma)
		candidate_array.append(simulated)
	print('{:<30}\t{}\t{}\t{}\t{}'
			.format(candidate, mu, np.mean(candidate_array), sigma, np.std(candidate_array)))