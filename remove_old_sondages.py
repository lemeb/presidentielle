import csv

sondages_raw = csv.DictReader(open('raw/sondages_1.csv'))
sondages_headers = sondages_raw.fieldnames

# SOCP = Sondages Only Candidates Polls

def all_candidates_present(row):
	if (row['Melenchon'] != '' and row['Macron'] != ''
	    and row['LePen'] != '' and row ['Hamon'] != ''
	    and row['Fillon2'] != ''):
		return True
	return False 

socp_array = []
for row in sondages_raw:
	if all_candidates_present(row):
		socp_array.append(row)

socp_f = open('data/socp.csv', 'w')

writer = csv.DictWriter(
    socp_f, sondages_headers)
writer.writeheader()
writer.writerows(socp_array)
socp_f.close()
