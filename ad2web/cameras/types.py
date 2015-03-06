# -*- coding: utf-8 -*-

from flask import current_app
import urllib
import numpy as np
import os
try:
    import cv2
    hascv2 = True
except ImportError:
    hascv2 = False

from .models import Camera
from .constants import USERNAME, PASSWORD, JPG_URL, CAMDIR, HEAD, FOOT, RECT_XML_FILE, READ_BYTE_AMOUNT

class CameraSystem(object):
    def __init__(self):
        self._cameras = {}
        self._camera_ids = []
        self._image_bytes = {}
        self._init_cameras()

    def _init_cameras(self):
        for cam in Camera.query.all():
            cam_info = [cam.username, cam.password, cam.get_jpg_url]
            self._cameras[cam.id] = cam_info
            self._image_bytes[cam.id] = ''
            self._camera_ids.append(cam.id)

    def get_camera_ids(self):
        return self._camera_ids

    def refresh_camera_ids(self):
        del self._camera_ids[:]
        for cam in Camera.query.all():
            self._camera_ids.append(cam.id)

    def write_image(self, id):
        if hascv2 == True:
            user_pass = self._cameras[id][USERNAME] + ':' + self._cameras[id][PASSWORD] + '@'
            url_slash_index = self._cameras[id][JPG_URL].find('//')

            if url_slash_index != -1:
                url_slash_index += 2
                stream_url = self._cameras[id][JPG_URL][:url_slash_index] + user_pass + self._cameras[id][JPG_URL][url_slash_index:]
                stream = urllib.urlopen(stream_url)
                cascade = cv2.CascadeClassifier(RECT_XML_FILE)

                #read the camera stream, hopefully capture a picture
                while self._image_bytes[id].find(FOOT) == -1:
                    self._image_bytes[id] += stream.read(READ_BYTE_AMOUNT)

                #find header
                head = self._image_bytes[id].find(HEAD)
                #find footer
                foot = self._image_bytes[id].find(FOOT)

                #header and footer present = full image
                if head != -1 and foot != -1:
                    #grab all bytes that represent a jpg, ignore http headers (+2 to actually include footer bytes)
                    jpg = self._image_bytes[id][head:foot+2]

                    #if we've created a jpg, let's go ahead and reset bytes buffer
                    self._image_bytes[id] = '' 

                    #create an image from the jpg bytes
                    img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)

                    #determine rectangles for face recognition, if present, draw a rectangle around the face
                    rects = cascade.detectMultiScale(img, 1.1, 5, cv2.cv.CV_HAAR_SCALE_IMAGE, (10, 10) )

                    if len(rects) != 0:
                        for x, y, w, h in rects:
                            cv2.rectangle(img, (x, y), (x+w, y+h), (127, 255, 0), 2)

                    if not os.path.exists(CAMDIR):
                        os.makedirs(CAMDIR)

                    #write camera image to temp directory "/tmp/cameras/cam1.jpg" for Camera ID 1 by default
                    cv2.imwrite(CAMDIR + '/cam' + str(id) + '.jpg', img)

