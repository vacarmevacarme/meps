# Projet

L'application `get_meps.py` permet de requêter une API mise à disposition par le parlement européen afin d'obtenir les données administratives des membres du parlement (MEPS) sous format CVS.

# Dépendances
- requests
- pandas
- datetime.date
- logging

# Démarche

## 1. Documentation API

Il faut d'abord trouver dans la doc de l'API :
- le protocole de l'API: REST est le plus commun mais il en existe d'autre comme graphQL
- *l'endpoint* où envoyer la demande: pour une API REST, ce sera un URL,
- les types de paramètres compatibles pour filtrer les données dès la requête à l'API,
- le mode d'authentification car une API est rarement ouverte,
- le format de la réponse que l'API nous donnera pour la décoder avec la bonne méthode. La plupart du temps JSON mais peut aussi être XML ou CSV,
- la schéma des données `{meta:...,body:[...],...}` et la <u>clé</u> qui permet de séparer le *body* des métadonnées, elles-aussi contenues dans la réponse.

Disons ici que:
- nous avons affaire à une API REST ouverte, 
- l'*endpoint* est un URL : https://europeanparliament.com/api/meps,
- le paramètre pour filtrer les ID est `meps/{mep_id}` et est un entier, et l'API supporte le paramètre `fields` pour uniquement sélectionner les champs désirés, ici: *id, givenName, familyName, citizenship.iso3, bday, deathDate* (où iso3 est une propriété de citizenship)

> Exemple d'URL à requêter: https://europeanparliament.com/api/meps/10?fields=id,givenName,familyName,citizenship.iso3,bday,deathDate,

- le format de la réponse sera `application/json` ,
- le schéma comportera une clé `'data'`qui permet d'extraire la liste des MEPS (*body*) de la réponse.

## 2. Application python

### Process

L'application sera orchestrée par un cron job une fois par jour. Comme elle tournera en arrière plan, nous avons besoin d'un script assez robuste pour:
- minimiser les erreurs, 
- gérer les exceptions,
- logger pour enquêter rapidement en cas d'erreur.


L'application suit la structure suivante:

1. Pour chaque MEP ID d'une liste variable:

   - Requête à l'API
   - Décodage en json
   - Extraction uniquement du *body* avec la clé `data`
   - Concatenage dans une une liste puis transformation en `pandas.DataFrame`

2. Sauvegarde les données CSV dans le sous-dossier `data/`

### Logging et robustesse

- Certaines étapes et les erreurs sont loggées avec la librairie `logging` dans un fichier `log.log`. 

- Les erreurs sont gérées grâce au `try/except` pour ne pas bloquer le script.


## 3. Cron job

Pour un tâche exécutée tous les matins à 8h depuis un environnement virtuel python, où les erreurs sont envoyées vers un fichier texte `cron_debug.txt`:

```
0 8 * * * MY_PATH/.venv/bin/python3 MY_PATH/meps/get_meps.py >> MY_PATH/cron_debug.txt 2>&1
```

# Problèmes rencontrés

- Je requêtais d'abord toutes les données à l'API pour les filtrer ensuite chez le client (avec duckdb par exemple). Mais le serveur peut déjà faire une grande partie du travail, ce qui prend beaucoup moins de temps pour recevoir les infos si ce sont de gros volumes de données. Certaines API ne supportent pas le filtrage avec `?fields=...`, il faudra alors filtrer côté client avec `pandas` ou des librairies `pySQL`
- Il y a plusieurs protocoles pour les API. Je me suis exercé sur des API REST car visiblement, elles sont les plus communes. Mais je comprends qu'il y en a d'autres et il faudra que je puisse m'adapter à toutes.
- Les APIs ne renvoient pas toutes le même schéma de données dans leur réponse et pas les mêmes clés ('data','results','items'...) associées à la liste des données que l'on cherche. Je trouve que cela fragilise un peu le script de la conserver en tant que constante, mais je ne sais pas si c'est un problème courant de voir la clé changer côté serveur.

# Pour aller plus loin

- Une API étant rarement ouverte, il faudra ajouter des données d'authentification dans un *header* lors de la commande `requests.get()`.
- On peut s'assurer que le CSV est sauvegardé au bon endroit avec la librairie `path`, peu importe sur quelle machine nous sommes.

# Commentaire

Ce genre de projet m'amuse beaucoup donc j'ai pris le temps d'en faire un peu plus avec la gestion des erreurs et le logging.
Pour avoir eu affaire à beaucoup de scripts automatisés (notamment en plateforme de test), les manques de lisibilité, de log et de robustesse sont souvent un problème. Donc de manière générale, j'essaie toujours de créer des scripts modulaires, bien compartimentés pour faciliter la relecture, la réutilisation et la maintenance. Mais si le mot d'ordre est la simplicité, j'irai plus droit au but évidemment.