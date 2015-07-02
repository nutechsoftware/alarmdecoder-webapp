# -*- coding: utf-8 -*-

from flask import current_app
import urllib
import os
try:
    import cv2
    import numpy as np
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
        self._xml_path = os.path.join(os.getcwd(), 'ad2web', 'cameras', RECT_XML_FILE)
        self._init_cameras()

    def _init_cameras(self):
        for cam in Camera.query.all():
            self._cameras[cam.id] = [cam.username, cam.password, cam.get_jpg_url]
            self._image_bytes[cam.id] = ''
            self._camera_ids.append(cam.id)

        current_app.jinja_env.globals['cameras'] = len(self._cameras)

    def get_camera_ids(self):
        return self._camera_ids

    def refresh_camera_ids(self):
        self._camera_ids = []
        self._cameras.clear()

        self._init_cameras()

    def write_image(self, id):
        if hascv2 == True:
            user_pass = self._cameras[id][USERNAME] + ':' + self._cameras[id][PASSWORD] + '@'
            url_slash_index = self._cameras[id][JPG_URL].find('//')

            if url_slash_index != -1:
                url_slash_index += 2
                stream_url = self._cameras[id][JPG_URL][:url_slash_index] + user_pass + self._cameras[id][JPG_URL][url_slash_index:]
                stream = urllib.urlopen(stream_url)
                cascade = cv2.CascadeClassifier(self._xml_path)

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
                    img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 1)

                    #determine rectangles for face recognition, if present, draw a rectangle around the face
                    rects = cascade.detectMultiScale(img, 1.1, 5, 2, (10, 10) )

                    if len(rects) != 0:
                        for x, y, w, h in rects:
                            cv2.rectangle(img, (x, y), (x+w, y+h), (127, 255, 0), 1)

                    if not os.path.exists(CAMDIR):
                        os.makedirs(CAMDIR)

                    #write camera image to temp directory "/tmp/cameras/cam1.jpg" for Camera ID 1 by default
                    cv2.imwrite(CAMDIR + '/cam' + str(id) + '.jpg', img)
