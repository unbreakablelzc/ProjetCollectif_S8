#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import numpy as np
import sys
import csv

# Gère l'export des données
class Export:

    def __init__(self, video, unAlgo, ma_liste):
        self.video = video
        self.algo = unAlgo
        self.donnees = ma_liste

    # Permet d'exporter les données du traitement dans un fichier CSV
    def export_CSV(self):
        if ('distance' in str(self.algo)):
            Algo = 'Distance'
        else:
            Algo = 'FlotsOptiques'
        fname = './resultats/Resultat.csv'
        csvfile = open(fname, "ab")
        writer = csv.writer(csvfile, delimiter=',')
        x = np.array(self.donnees)
        y = x.tolist()
        Max = str(max(y))
        Min = str(min(y))
        Moyen = str(sum(y) / len(self.donnees))
        localtime = time.asctime(time.localtime(time.time()))
        writer.writerow([self.video, localtime, Algo, Min, Max, Moyen])
        csvfile.close()