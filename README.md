# SR2I208
Projet de SR2I208 - 2019 : Détecter des données malicieuses à l'aide d'un Réseau de Neurones

## Création des fichiers test_x et validation_x
Utiliser de préférence BDD_thread.py

## Génération du fichier txt à partir de la base de données en CSV
L'utilisation de `BDD_thread.py` est fortement conseillée. Cette technique empêche de surcharger la RAM.

## Génération des batchs à partir du fichier txt
* Si plus de 4 Go de RAM : utiliser gener_batch.py
* Si moins utiliser : gener_batch_mem_eco.py. Il est plus lent mais largement moins gourmand en ressources
* TODO : pour aller plus loin, faire une version hybride
