#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
import cv2
import zone_interet as zi

# Gère l'affichage de la fenetre de selection de la Zi
class fen_zone_interet:

    # initialise la fenêtre de Zone Interet
    def __init__(self):

        dialog = Gtk.FileChooserDialog("Veuillez choisir une vidéo", None, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Valider", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_current_folder("./")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            self.get_one_image_from_video(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    # extrait une image de la vidéo selectionnée
    def get_one_image_from_video(self, video):
        video_capture = cv2.VideoCapture(video)
        # TODO : bien récupérer la dernière frame
        nb_frame = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_COUNT, int(nb_frame - 1))
        _, self.image = video_capture.read()
        cv2.imwrite("./zi/image_modele.png", self.image)
        self.show_ZI_window()

    def show_ZI_window(self):
        select_zi = zi.ZoneInteret()
        select_zi.show_window()


if __name__ == "__main__":
    print (" ERREUR:Ce fichier n'est pas le script pincipal. ")
    print (" Veuillez lancer le script principal. ")
