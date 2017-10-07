#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import cv2
import os
from collections import deque
from PIL import Image
from gi.repository import Gtk, GdkPixbuf, Gdk
import numpy as np


class detection_operator:

    def __init__(self):
        pass

    def isoler_operateur(self, video, lowH, highH):
        if os.path.exists(video):
            cap = cv2.VideoCapture(video)
            pts = deque(maxlen=12)

            print("avant while")
            print("lowH : "+str(lowH))
            print("highH :"+str(highH))
            start_frame = 3
            flag = True
            compteur = 0
            while flag:
                compteur = compteur + 1
                print(compteur)
                ret, frame = cap.read()
                if ret:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    lower_color = np.array([lowH, 100, 100])
                    upper_color = np.array([highH, 255, 255])
                    mask = cv2.inRange(hsv, lower_color, upper_color)
                    # LISSAGE
                    mask = cv2.erode(mask, None, iterations=2)
                    mask = cv2.dilate(mask, None, iterations=2)
                    result = cv2.bitwise_and(frame, frame, mask=mask)

                    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                    center = None
                    if len(cnts) > 0:
                        c = max(cnts, key=cv2.contourArea)
                        ((x, y), radius) = cv2.minEnclosingCircle(c)
                        M = cv2.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    # update the points queue
                    pts.appendleft(center)
                    bool = 0
                    for i in xrange(1, len(pts)):
                        if pts[i - 1] is None or pts[i] is None:
                            # Operateur n'est pas present
                            flag = False
                            continue
                        else:
                            # Operateur est present
                            if bool == 0:
                                start_frame = start_frame + 1;
                                bool = 1

                    #image = Image.fromarray(result, 'RGB')
                    #image.save("tmp.jpeg")
                    #self.GTKImage.set_from_file("tmp.jpeg")
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
                        # If the number of captured frames is equal to the total number of frames, we stop
                        break

            print("frame finale :"+str(start_frame))
            #self.GTKImage.set_from_file("")
            return start_frame

        else:
            message = Gtk.MessageDialog(type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK)
            message.set_markup("Veuillez choisir un video d'abord!")

            message.run()
            message.destroy()