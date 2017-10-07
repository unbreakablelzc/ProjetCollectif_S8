#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import algo
import os.path
import cv2
import sys
import numpy as np
import math
import zone_interet as zi

# On initialise les parametres de la fonction Shi-Tomasi qui detecte des points d'interet selon les coins reperes
#     - maxCorners : le nombre de points d'interet maximum dans la video
#     - qualityLevel : le niveau de qualite de la detection
#     - minDistance : la distance minimum entre deux points d'interets 
#     - blockSize : taille du block (patch) de dectection d'un coin (nombre de pixel)
feature_params = dict(maxCorners=10, \
                      qualityLevel=0.5, \
                      minDistance=10, \
                      blockSize=3)
# On initialise les parametre de la fonction de lucas kanade pour le flux optique
#    - winSize :
#    - maxLevel :
#    - criteria :
lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# On cree des valeurs aleatoire pour la colorisation des vecteurs sur notre video
color = np.random.randint(0, 255, (100, 3))


class algo_flots_optiques(algo.algorithme):  # hérite de la classe algo

    def get_nomAlgo(self):
        return "flots optiques"

    def traiterVideo(self, video, start_frame):

        ma_liste = list()
        debug = False
        if type(video) is str:
            cap = cv2.VideoCapture(video)
        else:
            cap = video

        # Detection de l'opérateur
        # On ne commence le traitement sur la première image dépourvu d'opérateur
        # On Passe les images
        # tant que l'indice ne correspond pas à ce que la méthode isoler_operateur() nous a renvoye plus tôt
        for i in range(0, start_frame):
            cap.read()

        # On prend la premiere image et on detecte les points d'interets
        ret, old_frame = cap.read()
        ret, frame = cap.read()

        # Detection de la zone d'intérêt si elle a été créée
        if zi.ZoneInteret.verifier_presence_fichier_ini() :
            with open("./zi/param.ini", "r") as file:
                line = file.readline()
                param = [int(x.strip()) for x in line.split(',')]
            frame = frame[param[1]:param[1] + param[3], param[0]:param[0] + param[2]]
            old_frame = old_frame[param[1]:param[1] + param[3], param[0]:param[0] + param[2]]

        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

        # On cree un masque pour le dessin
        if debug:
            mask = np.zeros_like(old_frame)

        vecteurs = 0
        nb_vecteurs = 0
        while (ret):
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # On calcule les nouvelles position grace au calcule du flux optique
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

            # On selectionne les anciennes et les nouvelles positions de nos points d'interet
            if p1 == None:
                break
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            # On dessine pour chaque point le vecteur dans la video et on realise un calcul pour determiner le nombre de vecteurs total
            # et la distance parcourue totale par tous les vecteurs
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                # On met dans 'a' la position x de la nouvelle position d'un point d'interet et dans 'b' sa position en y
                # On met dans 'c' la position x de l'ancienne position d'un point d'interet et dans 'd' sa position en y
                a, b = new.ravel()
                c, d = old.ravel()
                norme = math.sqrt((a - c) ** 2 + (b - d) ** 2)
                if norme >= 0:
                    vecteurs += norme
                    nb_vecteurs += 1
                if debug:
                    cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
                    cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
            ma_liste.append(norme / nb_vecteurs)
            vecteurs = 0
            nb_vecteurs = 1

            if debug:
                img = cv2.add(frame, mask)
                cv2.imshow('frame', img)
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    exit(1)
            # On passe a l'image suivante dans la video
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)
            # On lit chaque nouvelle image de la video pour effectuer notre traitement
            ret, frame = cap.read()

            # On applique les paramètres à chaque frame
            if ret and zi.ZoneInteret.verifier_presence_fichier_ini():
                frame = frame[param[1]:param[1] + param[3], param[0]:param[0] + param[2]]

        if debug:
            cv2.destroyAllWindows()
            cap.release()
        return ma_liste


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
            USAGE: ./algo_flots_optiques.py coefflissage
        """
        exit(1)
    test(int(sys.argv[1]))
