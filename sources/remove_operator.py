#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import deque
import cv2
import numpy as np

def fn_remove_operator(path_video):
    cap = cv2.VideoCapture(path_video)
    #size of the video width and height
    w = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ))
    h = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ))
    
    # video recorder
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    outName = 'tmp_video_without_operator.avi'
    video_writer = cv2.VideoWriter(outName, fourcc, 100, (w, h))
    
    pts = deque(maxlen=12)
    # define range of yellow color in HSV
    lower_yellow = np.array([23,46,133])
    upper_yellow = np.array([40,150,255])
    
    while not cap.isOpened():
        cap = cv2.VideoCapture(path_video)
        cv2.waitKey(1000)
        print "Wait for the header"
    
    pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
    
    while True:
        flag, frame = cap.read()
        if flag:
            # The frame is ready and already captured
            #cv2.imshow('video', frame)
            #frame = cv2.flip(frame, 0)
            hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv,lower_yellow, upper_yellow)
            #lissage
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
            #result = cv2.bitwise_and(frame,frame,mask = mask)
            #contour
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            
            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # update the points queue    
            pts.appendleft(center) 
             # loop over the set of tracked points
            for i in xrange(1, len(pts)):
                # if either of the tracked points are None,
                # them
                if pts[i - 1] is None or pts[i] is None:
                    #operator is not present in the video
                    #Creating a new tempory video without operator
                     video_writer.write(frame)
                     continue
                else:
                    #Operator is present in the video
                    pass
                   
            pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
            # It is better to wait for a while for the next frame to be ready
            #scv2.waitKey(1000)
    
        if cv2.waitKey(10) == 27:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
            # If the number of captured frames is equal to the total number of frames,
            # we stop
            break
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
    return outName