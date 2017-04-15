# Présidentielle 2017

## Cf. article sur les sondages caviardés

Voilà comment vérifier et reproduire les résultats:

1. `pip install pandas matplotlib numpy scipy` 
2. `python3 inspect_herding_2017.py` 

Vous pouvez changer la variable PLOT à la ligne 20 pour voir ou ne pas voir des graphiques associés aux résultats. Ce qui est affiché sur la console correspond à :

(Nom du candidat) (Nb de sondages pré-25 fev. dans l'intervalle) (Nb de sondages pré-25 fev. hors intervalle) Nb de sondages post-25 fev. dans l'intervalle) (Nb de sondages post-25 fev. hors intervalle)
Chi-square test des sondages pré-25 février 
Chi-squre test des sondages post-25 février