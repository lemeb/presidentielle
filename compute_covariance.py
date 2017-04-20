import csv, pandas, json, random
from pandas import DataFrame as pDF 
import numpy as np
from scipy.stats import pearsonr, norm
from itertools import combinations, combinations_with_replacement
from lowess import lowess
import matplotlib.pyplot as plt
import seaborn as sns

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
favoris = ['Macron', 'Melenchon', 'LePen', 'Fillon']
petits = ['Lassalle', 'Asselineau', 'Cheminade', 'DupontAignan', 'Arthaud', 'Poutou']


### DATA PREPARATION


# Importer
sondages = csv.DictReader(open('data/sondages_17.csv'))
sondages_array = []
for sondage in sondages:
	sondages_array.append(sondage)
df_so = pDF(sondages_array)


# Clean 
def cleanfunc(row): return row.apply(lambda s: 0. if s == '' else float(s))
df_so.loc[:, candidats] = df_so[candidats].apply(cleanfunc, axis=1)
df_so.loc[:, 'DaysBefore'] = df_so['DaysBefore'].apply(int)
df_so.loc[:, 'N'] = df_so['N'].apply(int)
df_clean = df_so[(df_so['Jadot'] == '') & (df_so['Bayrou'] == '')]


# Normalize
def normalize(row, total=100): 
	return row[candidats].apply(lambda val: val * (total/row['sum']))
df_clean.loc[:,'sum'] = df_clean.loc[:,candidats].sum(axis=1)
df_clean.loc[:, candidats] = normalize(df_clean)


### WEIGHTED AVERAGE
weightedAverageActivated = True
correlatedActivated = True

## First option: 
## local regression

F_FOR_CANDIDAT = 0.3
F_FOR_PETIT = 0.67

LR_AVG = pandas.Series(index=candidats)
for candidat in candidats:
	# x = np.array(df_clean['DaysBefore'])
	x = np.linspace(0.0, 1.0, num=len(df_clean))
	y = np.array(df_clean[candidat])
	f = F_FOR_PETIT if candidat in petits else F_FOR_CANDIDAT
	candidat_lowess = lowess(x,y, f=f)
	LR_AVG[candidat] = candidat_lowess[-1]
	# plt.plot(x,candidat_lowess, label=candidat)
# plt.legend(loc='best')
# plt.show()


## Second option: 
## Weight by time, sample size (hl means half-life)

TIME_HL_FACTOR = 4       # By how much the weigh will be divided by
TIME_HL_DURATION = 5     # In days
INSTITUTE_HL_PENALTY = 4 # By how much the weigh is divided by 
						 # for each new survey by the same polling company
FACTOR_SAMPLESIZE = 0.4

# Time
last_survey_day = pDF.min(df_clean['DaysBefore'])
def half_lifing(d_before):
	return 1 / (TIME_HL_FACTOR ** ((d_before - last_survey_day) / TIME_HL_DURATION))
df_clean.loc[:,'WeightTime'] = df_clean['DaysBefore'].apply(half_lifing)

# Penaliser les sondages d'un même institut
df_clean.loc[:, 'SameInstituteWeight'] = np.ones(len(df_clean))
for institut in set(df_clean['Institut']):
	def ins_weight(list_candidates):
		length = len(list_candidates)
		list_candidates = list_candidates * (list(reversed(range(0,length))))
		list_candidates = list_candidates.apply(
			lambda val: 1 / (INSTITUTE_HL_PENALTY ** val))
		return list_candidates

	label = df_clean['Institut'] == institut, 'SameInstituteWeight'
	df_clean.loc[label] = (ins_weight(df_clean.loc[label]))

# Take sample size into account
mediane_sondages = np.median(df_clean['N'])
def w_sam(size): return (size / mediane_sondages) ** FACTOR_SAMPLESIZE
weight_sample_survey = df_clean['N'].apply(w_sam)
df_clean.loc[:, 'WeightSize'] = weight_sample_survey

# Apply the weighted average
df_clean.loc[:, 'CombinedWeight'] = (
	df_clean['WeightSize'] * df_clean['WeightTime'] * df_clean['SameInstituteWeight'])
def apply_weighted_average(row):
	return (row[:-1].apply(lambda val: val * row['CombinedWeight']))
	# row[:-1] is here to avoid combinedweight
c_and_cw = candidats + ['CombinedWeight']
weighted_average = df_clean[c_and_cw].apply(apply_weighted_average, axis=1).sum(axis=0)
WE_AVG = weighted_average / df_clean['CombinedWeight'].sum()


AVG_M = WE_AVG if weightedAverageActivated else LR_AVG


## CORRELATION MATRIX


# Cov matrix & Correlation matrix 
cov_matrix = df_clean[candidats].cov()
corr_matrix = df_clean[candidats].corr()
# Correlation matrix w/ pvalue
corr_matrix_with_pvalue = pDF(index=candidats, columns=candidats)
pvalues = pDF(index=candidats, columns=candidats)
for candidat1, candidat2 in list(combinations_with_replacement(candidats, 2)):
	corr_pvalue = pearsonr(df_clean[candidat1], df_clean[candidat2])
	corr_matrix_with_pvalue[candidat1][candidat2] = corr_pvalue
	corr_matrix_with_pvalue[candidat2][candidat1] = corr_pvalue
	pvalues[candidat1][candidat2] = corr_pvalue[1]
	pvalues[candidat2][candidat1] = corr_pvalue[1]
if correlatedActivated: 
	cov_matrix.to_csv('data/covariance.csv')
	corr_matrix.to_csv('data/correlation.csv')
	pvalues.to_csv('data/pvalues.csv')
eigen_corr, norm_eigen = np.linalg.eig(corr_matrix)



### SIMULATION



SIMULATION_N = 10000
# Je prends 2/3 de la mediane car difference entre intention de votes
# et échantillon total
REDUCTION_MEDIANE_SONDAGES = (2/3)
ENTROPY = (6/2.6)

tab_string = '{:<20}   {:<20}   {:<20}   {:<20}   {:<20}   {:<20}'

def get_deviation(score):
	mediane = REDUCTION_MEDIANE_SONDAGES * mediane_sondages
	z_critical = norm.ppf(q = 1-(1-0.95)/2)
	result = z_critical * np.sqrt((score * (100 - score)) / mediane)
	return result * ENTROPY

header = tab_string.format(
	"Candidat", "Moyenne sondages", "Moyenne local reg", 
	"Moyenne simulation", "Std attendue", "Std simulations")

## Première option
## aucune corrélation

all_candidates_array = []
if not correlatedActivated:
	print(str(SIMULATION_N) + " simulations  -- Univariate")
	print(header)

for candidat in AVG_M.index.values:
	candidat_array = []
	mu = AVG_M[candidat]
	sigma = get_deviation(mu)
	for i in range(SIMULATION_N):
		simulated = random.gauss(mu, sigma)
		candidat_array.append(0.0 if simulated < 0 else simulated)
	all_candidates_array.append(candidat_array)
	if not correlatedActivated:
		print(tab_string.format(
			candidat, WE_AVG[candidat], LR_AVG[candidat], 
			np.mean(candidat_array), sigma, np.std(candidat_array)))

# Normalize
df_sim = pDF(all_candidates_array, index=candidats).T
df_sim.loc[:,'sum'] = df_sim.sum(axis=1)
# df_sim_normalized
df_sn = normalize(df_sim)
# print(df_sim)

## Deuxième option
## Corrélation

# I know it's ugly
matrix_of_zeroes = pDF(np.zeros((len(candidats), len(candidats))), index=candidats, columns=candidats)
MATRIX = corr_matrix
# Adjust variance
for candidat in candidats:
	MATRIX[candidat][candidat] = get_deviation(AVG_M[candidat])
print(MATRIX)
corr_simulated = []
for i in range(SIMULATION_N):
	simulated_numbers = np.random.multivariate_normal(AVG_M, MATRIX)
	corr_simulated.append(simulated_numbers)

# df_sim_normalized_and_correlated
df_sc = pDF(corr_simulated, columns=candidats)
df_sc.loc[:,'sum'] = df_sc.sum(axis=1)
df_snc = normalize(df_sc)
df_snc.loc[:,'sum_petits'] = df_snc[petits].sum(axis=1)

# Print
if correlatedActivated:
	print(str(SIMULATION_N) + " simulations  -- Multivariate")
	print(header)
	for candidat in candidats:
		candidat_array = np.array(df_snc.loc[:,candidat])
		sigma = MATRIX[candidat][candidat]
		print(tab_string.format(
			candidat, WE_AVG[candidat], LR_AVG[candidat], 
			np.mean(candidat_array), sigma, np.std(candidat_array)))

# J'hésite franchement à fusionner les petits candidats...

# Viz
for candidat in candidats:
	plt.hist(list(df_snc.loc[:,candidat]), alpha=0.5, bins=60, label=candidat)
	plt.legend(loc='best')
plt.show()


DF_REF = df_snc if correlatedActivated else df_sn



### STATISTICS



df_ranked = DF_REF.rank(axis=1, ascending=False).apply(lambda x: x.apply(int))
for candidat in candidats:
	df_ranked.loc[:, candidat+'Q'] = df_ranked.apply(
		lambda row: row[candidat] == 1 or row[candidat] == 2, axis=1)

print("weighted? {} correlated? {}".format(weightedAverageActivated,correlatedActivated))
for candidat1, candidat2 in combinations(favoris, 2):
	df_ranked.loc[:, candidat1+candidat2] = df_ranked.apply(
		lambda row: row[candidat1+'Q'] and row[candidat2+'Q'], axis=1)
	df_second_tour = df_ranked.loc[df_ranked[candidat1+candidat2] == True]

	print("{:<20}\t{}".format(
		candidat1 + " v " + candidat2, 
		len(df_second_tour) / SIMULATION_N))
	print("     {:<15}\t{}".format(
		candidat1 + " en tête", 
		len(df_second_tour.loc[df_second_tour[candidat1] == 1])/SIMULATION_N))
	print("     {:<15}\t{}\n--------".format(
		candidat2 + " en tête", 
		len(df_second_tour.loc[df_second_tour[candidat2] == 1])/SIMULATION_N))
