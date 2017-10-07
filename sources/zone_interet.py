# -*- coding: utf-8 -*-
import os.path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
from gi.repository import Gtk, GdkPixbuf, Gdk


class ZoneInteret:

    @staticmethod
    def verifier_presence_fichier_ini():
        return os.path.isfile('./zi/param.ini')

    @staticmethod
    def supprimer_ZI(window):
        md = Gtk.MessageDialog(window, None, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.YES_NO,
                               "Etes-vous sûr de vouloir supprimer la Zone d'intérêt actuelle ?")
        response = md.run()
        if response == Gtk.ResponseType.YES:
            if ZoneInteret.verifier_presence_fichier_ini():
                try:
                    os.remove("./zi/param.ini")
                    os.remove("./zi/image_modele.png")
                    os.remove("./zi/image_zone_interet.png")
                except OSError, e:
                    error = Gtk.MessageDialog(window, None, Gtk.MessageType.ERROR,
                                              Gtk.ButtonsType.CLOSE,
                                              "Impossible de supprimer les fichiers dans le repertoire /zi")
                    error.run()
                    error.destroy()

        md.destroy()
        
    # Initialise les variables nécessaires à l'affichage de l'image et aux événements
    def __init__(self):
        # On se sert de l'image extraite précédemment
        self.img = mpimg.imread('./zi/image_modele.png')

        # On initialise le titre de la fenêtre
        fig = plt.figure(1)
        fig.canvas.set_window_title("Zone Interet")

        # On récupère les infos des axes
        self.ax = plt.gca()

        # On initialise le futur rectangle dessiné (non rempli aux bordures rouges)
        self.rect = Rectangle((0,0), 1, 1, fill=False, edgecolor="red")

        # Initialisation des points du rectangle
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.ax.add_patch(self.rect)

        # Liaison des événements
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_mouseclick_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_mouseclick_release)
        self.ax.figure.canvas.mpl_connect('key_press_event', self.on_keyboard_press)

        # Affichage de l'image dans la fenêtre
        self.imgplot = plt.imshow(self.img)

    # Un click gauche -> sauvegarde des coordonnées du pointeur
    def on_mouseclick_press(self, event):
        self.x0 = event.xdata
        self.y0 = event.ydata

    # Click gauche relâché -> dessin du rectangle
    def on_mouseclick_release(self, event):
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        self.ax.figure.canvas.draw()

    # Si la touche "enter" est appuyée, on sauvegarde la zone d'intérêt
    def on_keyboard_press(self, event):
        if event.key == 'enter':
            with open("./zi/param.ini", "w") as file:
                file.write(str(int(self.rect.get_x()))+",")
                file.write(str(int(self.rect.get_y()))+",")
                file.write(str(int(self.rect.get_width())) + ",")
                file.write(str(int(self.rect.get_height())))

            # On cache les axes avant d'enregistrer l'image modele avec la zone d'interet
            self.ax.get_xaxis().set_visible(False)
            self.ax.get_yaxis().set_visible(False)
            plt.title("Zone interet")
            plt.savefig("./zi/image_zone_interet.png")
            plt.close()
            message = Gtk.MessageDialog(type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Une nouvelle Zone d'intérêt a été saisie !")
            message.run()
            message.destroy()

    def show_window(self):
        plt.title("Selectionner la zone interet avec la souris. Appuyez sur entrer pour valider.")
        plt.show()






