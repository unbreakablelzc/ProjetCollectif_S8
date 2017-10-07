#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk


class fen_about:
    interface=0

    def __init__(self):
        self.interface = Gtk.Builder()
        self.interface.add_from_file('ui_about.glade')

        self.interface.connect_signals(self)
        self.interface.get_object("aboutdialog").show_all()

    def on_aboutdialog_response(self, widget,pomme):
        self.interface.get_object("aboutdialog").destroy()


if __name__ == "__main__":
    print ("ERREUR:Ce fichier n'est pas le script pincipal.")
    print ("       Veuillez lancer le script principal.")
