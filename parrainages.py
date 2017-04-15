import json, sys
parrainages_fichier = open('/Users/L/Desktop/Conseil Constitutionnel/parrainages/parrainagestotal.json', encoding='utf-8')
parrainages_json = json.load(parrainages_fichier, encoding='utf-8')

arguments = sys.argv
arguments_ou_pas = True if len(sys.argv) > 1 else False

voir_toutes_conditions = False
voir_seulement_vainqueurs = False

if arguments_ou_pas:
	if arguments[1] == '-c':
		voir_toutes_conditions = True
	elif arguments[1] == '-v':
		voir_seulement_vainqueurs = True
	elif arguments[1] == '-cv' or arguments[1] == '-vc':
		voir_toutes_conditions = True
		voir_seulement_vainqueurs = True

for candidat in parrainages_json:
	nom = candidat['Candidat-e parrainé-e']
	parrainages = candidat['Parrainages']
	nb_parrainages = len(parrainages)
	if (nb_parrainages <= 500):
		if voir_seulement_vainqueurs:
			continue
		else:
			print('🚫 {:<30} a récolté seulement {:<3} parrainages'.format(nom, str(nb_parrainages)))
			if not voir_toutes_conditions:
				continue
	else:
		print('\n🎉 ' + nom + ' a récolté ses 500 parainnages...')
		print('\t(' + str(nb_parrainages) + ' pour être précis)')

	if not voir_toutes_conditions:
		print('')
		continue

	def départementDe(x):
		return x['Département']
	départements = [départementDe(x) for x in parrainages]
	compte_départements = {}
	for département in départements:
		if département in compte_départements:
			compte_départements[département] += 1
		else: 
			compte_départements[département] = 1
	compte_départements_sans_50 = {}
	for département in compte_départements:
		compte_départements_sans_50[département] = compte_départements[département]
		if (compte_départements[département] > 50):
			print('\t\tIl y a plus de 50 signatures dans le département ' + département + '...')
			compte_départements_sans_50[département] = 50
	if (sum(compte_départements_sans_50.values()) < 500
			and sum(compte_départements_sans_50.values()) != sum(compte_départements.values()) ):
		print('\t🚫 Le fait qu\'il y ait plus de 50 signatures dans un département invalide cette candidature.')
	else: 
		print('\t🎉 Pas plus d\'un dixième des candidatures ne provient d\'un seul département.')
	nb_départements = len(set(départements))
	if (nb_départements <= 30):
		print('\t🚫 ' + 'Ses parainnages proviennent de seulement ' + str(nb_départements) + '/30 départements\n')
		continue
	print('\t🎉 Les parrainages proviennent de 30 départements ou plus.')
	print('\t\t(' + str(nb_départements) + ' pour être précis)\n')
