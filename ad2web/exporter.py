import os
import platform
import hashlib
import io
import tarfile
import json
import re
import socket
import random
import compiler
import sys
import types
import importlib
import time

from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import SQLAlchemyError
from .utils import make_dir, tar_add_directory, tar_add_textfile
from .settings import Setting
from .settings.constants import EXPORT_MAP
from datetime import datetime, timedelta
from utils import INSTANCE_FOLDER_PATH
from flask import Response

class Exporter(object):
    EXPORT_PATH = os.path.join(INSTANCE_FOLDER_PATH, 'exports')
    DAY_SECONDS = 86400
    WRITE_MODE = 'w:gz'
    
    def __init__(self):
        self.prefix = 'alarmdecoder-export'
        self.export_path = Setting.get_by_name('export_local_path',default=self.EXPORT_PATH).value
        self.full_path = None
        self.fileobj = None
        self.filename = None

        if self.export_path != '' and not os.path.exists(self.export_path):
            os.makedirs(self.export_path)

    def exportSettings(self):
        self.fileobj = io.BytesIO()
        self.filename = '{0}-{1}.tar.gz'.format(self.prefix, datetime.now().strftime('%Y%m%d%H%M%S'))
        self.full_path = os.path.join(self.export_path, self.filename)

        with tarfile.open(name=bytes(self.filename), mode=self.WRITE_MODE, fileobj=self.fileobj) as tar:
            tar_add_directory(tar, self.prefix)

            for export_file, model in EXPORT_MAP.iteritems():
                tar_add_textfile(tar, export_file, bytes(self._export_model(model)), self.prefix)

    def writeFile(self):
        with open(self.full_path, self.WRITE_MODE) as out:
            out.write(self.fileobj.getvalue())

        return self.full_path

    def removeFile(self):
        if os.path.isfile(self.full_path):
            os.remove(self.full_path)

    def removeOldFiles(self, days):
        if self.export_path != '':
            current_time = time.time()
            cutoff = current_time - (days * self.DAY_SECONDS)

            files = os.listdir(self.export_path)
            
            for f in files:
                fullpath = os.path.join(self.export_path, f)
                if os.path.isfile(fullpath):
                    #file stats
                    t = os.stat(fullpath)
                    #creation time
                    c = t.st_ctime

                    # delete file if older than days
                    if c < cutoff:
                        os.remove(fullpath)

    def ReturnResponse(self):
        return Response(self.fileobj.getvalue(), mimetype='application/x-gzip', headers= { 'Content-Type': 'application/x-gzip', 'Content-Disposition': 'attachment; filename=' + self.filename } )

    def _export_model(self, model):
        data = []
        for res in model.query.all():
            res_dict = {}
            for c in class_mapper(res.__class__).columns:
                value = getattr(res, c.key)

                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S.%f')
                elif isinstance(value, set):
                    continue

                res_dict[c.key] = value

            data.append(res_dict)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), skipkeys=True)
