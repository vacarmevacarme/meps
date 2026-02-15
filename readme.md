# Projet

L'application `get_meps.py` permet de requêter une API mise à disposition par le parlement européen afin d'obtenir les données administratives des membres du parlement (MEPS) sous format CVS.

# Dépendances

- requests
- pandas
- duckdb
- datetime.date
- logging

# Démarche

## 1. Documentation API

Il faut d''abord trouver dans la doc de l'API :

- *l'endpoint* où envoyer la demande,
- le format de la réponse que l'API nous donnera pour la décoder avec la bonne méthode. La plupart du temps JSON mais peut aussi être XML ou CSV,
- la structure des données et la <u>clé</u> qui permet d'extraire de cette structure la liste des meps que nous cherchons.

Disons ici que l'endpoint est un URL, le format sera `application/ld+json` et la structure `{meta:...,data:[...])` aura une clé `'data'`qui donne accès à la liste des MEPS.

## 2. Application python
De manière générale, j'essaie toujours de créer des scripts modulaires, bien compartimentés pour faciliter la relecture et la réutilisation. Pour avoir eu à faire à beaucoup de scripts automatisés, le manque de log et la robustesse est toujours un problème. J'aurais fait un système moins 'overkill' pour un script one-shot.

### Process

L'application sera orchestrée par un cronjob une fois par jour. Comme elle tournera en arrière plan, nous avons besoin d'un script assez robuste pour:
- minimser les erreurs, 
- gérer les exceptions,
- logger pour enquêter rapidement en cas d'erreur.


L'application suit la structure suivante:

1. Requête à l'API
2. Décodage en json
3. Extraction uniquement des données recherchées avec la clé `data`
4. Formattage en `pandas.DataFrame`
5. Filtrage des champs désirés en sql avec `duckdb` (id, givenName, familyName, citizenship en ISO3* , bday, deathDate)
6. Sauvegarde en CSV

**disons que iso3 est une nested key de citizenship à laquelle on peut accéder en sql par `citizenship.iso3`*

### Logging et robustesse

- Certaines étapes et les erreurs sont loggées avec la librairie `logging` dans un fichier `log.log`.
- Les erreurs sont gérées grâce au `try/except` pour ne pas bloquer le script. Son point faible reste la clé `'data'` qui permet d'extraire les données et qui est une constante. Si les développeurs changent cette clé, aucune donnée ne pourra être trouvée sans modifier le script. Cependant, l'erreur sera gérée et loggée et aucun CSV ne sera généré.

## 3. Cron job

Pour un tâche exécutée tous les matins à 8h depuis un environnement virtuel python, où les erreurs sont envoyées vers un fichier texte `cron_debug.txt`:

```
0 8 * * * MY_PATH/.venv/bin/python3 MY_PATH/meps/get_meps.py >> MY_PATH/cron_debug.txt 2>&1
```

# Problèmes rencontrés

- Les APIs ne renvoient pas toutes la même structure de données dans leur réponse et pas les mêmes clés ('data','results','items'...) associées à la liste des données que l'on cherche. Cela fragilise un peu le script et le rend peu flexible.