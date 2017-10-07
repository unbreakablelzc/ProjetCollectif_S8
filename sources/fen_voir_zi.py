# -*- coding: utf-8 -*-
from gi.repository import Gtk, GdkPixbuf, Gdk
import zone_interet as zi

# Permet de voir une zone d'interet
class fen_voir_zi:

    # Initialise la fenetre et l'affiche
    def __init__(self):
        interface = Gtk.Builder()
        interface.add_from_file('ui_ZIVoir.glade')
        self.image = interface.get_object("imageZI")
        self.label = interface.get_object("param")
        self.window = interface.get_object("fen_voir_zi")

        # Presence du fichier "param.ini"
        if zi.ZoneInteret.verifier_presence_fichier_ini():
            with open("./zi/param.ini", "r") as file:
                line = file.readline()
                param = [x.strip() for x in line.split(',')]
            self.label.set_text("Paramètres de la zone rectangulaire (en pixel):\n"+
                                "x = " + param[2] + "\n" +
                                "y = " + param[0] + "\n" +
                                "longueur = " + param[3] + "\n" +
                                "largeur = " + param[1])
            self.image.set_from_file("./zi/image_zone_interet.png")
            self.window.show_all()
        else:
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Il n'y a pas de Zone d'intérêt disponible !")
            message.run()
            message.destroy()