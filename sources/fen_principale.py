#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, GdkPixbuf, Gdk
from gi.repository import GLib

from threading import Thread

import fen_about
import algo_distance
import algo_flots_optiques
import threading
import os.path
import time
import sys
import cv2
import remove_operator
import numpy as np
from collections import deque
from PIL import Image
import fen_zone_interet as fzi
import fen_voir_zi as fvzi
import zone_interet as zi
import subprocess
import os
import affichage_graphique
import Export


def thread(video, unAlgo, frame):
    ma_liste = unAlgo.traiterVideo(video, frame)
    pomme = affichage_graphique.affichage_graphique(video, frame)
    thread_video = threading.Thread(None, lancer_video, None, (),
                                    {'video': video})
    thread_video.start()
    pomme.afficher(ma_liste)
    export = Export.Export(video, unAlgo, ma_liste)
    export.export_CSV()



def lancer_video(video):
    subprocess.Popen([os.path.join("vlc"), os.path.join(video)])


class fen_principale:
    def __init__(self):
        # Initialise les variables utiles
        self.lowH = 0;
        self.highH = 0;
        self.start_frame = 3;

        # Initialise l'interface
        interface = Gtk.Builder()
        interface.add_from_file('ui_principale.glade')

        interface.connect_signals(self)
        self.window = interface.get_object("fen_principale")
        self.comboboxAlgo = interface.get_object("ui_comboboxtextAlgo")
        self.mycombobox = interface.get_object('comboboxtext1')

        self.algo = interface.get_object("Algo")
        self.video = interface.get_object("Video")
        self.spinner = interface.get_object("loading")
        self.textView = interface.get_object("textview1")
        self.GTKImage = interface.get_object("GTKImage")

        self.buttonSelectColor = interface.get_object("choose_color_button")
        self.buttonIsolerOperator = interface.get_object("btn_operator")
        self.buttonValider = interface.get_object('valider')
        self.buttonValider.set_sensitive(False)

        # Detection du fichier "param.ini"
        # S'il n'y est pas, c'est que la zone d'intérêt n'a pas été définie
        if not zi.ZoneInteret.verifier_presence_fichier_ini():
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Vous n'avez pas sélectionné de Zone d'intérêt pour les vidéos !")
            message.run()
            message.destroy()

    def on_mainWindow_destroy(self, window):
        Gtk.main_quit()
        sys.exit(0)

    # Gère l'appui du bouton pour lancer le traitement
    def on_myButton_clicked(self, widget):
        # Choix de l'algorithme
        self.textView.get_buffer().set_text("")
        algo = self.mycombobox.get_active() + 1

        # Si la vidéo existe, on lance un autre thread en exécutant le bon algo
        if (os.path.exists(self.video.get_text())):
            self.spinner.start()
            self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),
                                              "\n" + "Suppression de l'opérateur de la vidéo...")

            self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),
                                              "\n" + "Suppression terminé...")

            # Algorithme Distance
            if (algo == 1):
                self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),
                                                  "\n" + "Application de l'algorithme Distances...")
                a = threading.Thread(None, thread, None, (),
                                     {'video': self.video.get_text(), 'unAlgo': algo_distance.algo_distance(),
                                      'frame': self.start_frame})
                a.start()
                # Algorithme flotsoptiques
            elif (algo == 2):
                self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),
                                                  "\n" + "Application de l'algorithme flots optiques...")
                a = threading.Thread(None, thread, None, (), {'video': self.video.get_text(),
                                                              'unAlgo': algo_flots_optiques.algo_flots_optiques(),
                                                              'frame': self.start_frame})
                a.start()
            self.spinner.stop()
        else:
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Veuillez choisir un video d'abord!")

            message.run()
            message.destroy()

    def on_combobox_algo_changed(self, widget):
        print('choix algo')
        print(self.comboboxAlgo.get_active_text())

    def on_about_activate(self, menuitem):
        fen_about.fen_about()

    # Gère la sélection de la vidéo
    def on_choixdossier_clicked(self, widget):
        # choisir un dossier : Gtk.FileChooserAction.SELECT_FOLDER
        dialog = Gtk.FileChooserDialog("Veuillez choisir un dossier", self.window, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Valider", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_current_folder("./")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            self.video.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_Distance_activate(self, menuitem):
        self.algo.set_text("Distance")

    def on_FlotsOptiques_activate(self, menuitem):
        self.algo.set_text("FlotsOptiques")

    def on_SelectionnerZI_activate(self, menuitem):
        fzi.fen_zone_interet()

    def on_VoirZI_activate(self, menuitem):
        fvzi.fen_voir_zi()

    def on_SupprimerZI_activate(self, menuitem):
        zi.ZoneInteret.supprimer_ZI(self.window)


    # Permet de retourner la première image d'une vidéo ne comportant pas la couleur désirée
    def isoler_operator(self):
        self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),

                                              "\n" + "Detection de l'opérateur...")
        if (os.path.exists(self.video.get_text())):
            cap = cv2.VideoCapture(self.video.get_text())
            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret == True:
                    #Transformation en HSV
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    #Paramètres hsv pour isoler la couleur teinte, saturation, Valeur
                    #Teinte = couleur 
                    #Saturation : L'intensité de la couleur 
                    #Valeur : Brillance de couleur
                    lower_color = np.array([self.lowH, 100, 100])
                    upper_color = np.array([self.highH, 255, 255])
                    
                    mask = cv2.inRange(hsv,lower_color,upper_color)
                    kernel = np.ones((5,5),np.uint8)
                    #lissage pour enlever des éventuels bruits
                    erosion = cv2.erode(mask,kernel,iterations = 1)
                    #detection des contours de l'operateur
                    contours, hierarchy = cv2.findContours(erosion.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    if(len(contours) > 0 ):
                        #operateur présent 
                        cv2.drawContours(frame,contours,-1,(0,255,0),3)
                        self.start_frame = self.start_frame + 1
                        image = Image.fromarray(frame, 'RGB')
                        image.save("tmp.jpeg")
                        self.GTKImage.set_from_file("tmp.jpeg")
                    else:
                        break
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
                        # If the number of captured frames is equal to the total number of frames, we stop
                        break;

            self.GTKImage.set_from_file("")
            self.buttonValider.set_sensitive(True)
            self.textView.get_buffer().insert(self.textView.get_buffer().get_end_iter(),

                                              "\n" + "Opérateur détecté !")


        else:
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Veuillez choisir un video d'abord!")
            message.run()
            message.destroy()

    # Gère l'appui du bouton "Valider couleur"
    def on_btn_operator_clicked(self, event):
        self.textView.get_buffer().set_text("")
        color = self.buttonSelectColor.get_color()

        list1 = list(color.to_string())
        list2 = ['#', list1[1], list1[2], list1[5], list1[6], list1[9], list1[10]]
        toHex = ''.join(list2)
        RGB = self.hex_to_rgb(toHex)
        print toHex
        print RGB
        color = np.uint8([[[RGB[0], RGB[1], RGB[2]]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
        hue = hsv_color[0][0][0]
        self.lowH = hue - 10
        self.highH = hue + 10
        if self.lowH < 0:
            self.lowH  = 0
        if self.highH < 0:
            self.highH = 0
            
        if (os.path.exists(self.video.get_text())):
            self.isoler_operator()
        else:
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Veuillez choisir un video d'abord!")
            message.run()
            message.destroy()

    # Converti valeurs hexa en RGB
    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

if __name__ == "__main__":
    fen_principale()
    Gtk.main()
