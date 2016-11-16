try:
    import miniupnpc
    has_upnp = True
except ImportError:
    has_upnp = False

import threading
import time
from .extensions import db
from .settings.models import Setting

class UPNPThread(threading.Thread):
    TIMEOUT = 60 * 60 * 3   # 3 hour refresh

    def __init__(self, decoder):
        threading.Thread.__init__(self)
        self._decoder = decoder
        self.internal_port = Setting.get_by_name('upnp_internal_port',default=None).value
        self.external_port = Setting.get_by_name('upnp_external_port',default=None).value

        if has_upnp:
            self.upnp = UPNP(self._decoder)
        self._running = False

        with self._decoder.app.app_context():
            self._decoder.app.logger.info("UPNP Discovery Started")

    def stop(self):
        if self.upnp is not None:
            try:
                self.upnp.removePortForward(self.external_port)
            except Exception as e:
                pass
                #self._decoder.app.logger.info("UPNP Error: {0}".format(e))

        self._running = False

    def run(self):
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                if self.internal_port is not None and self.external_port is not None and self.upnp is not None:
                    try:
                        self.upnp.addPortForward(self.internal_port, self.external_port)
                    except Exception as e:
                        pass
                        #self._decoder.app.logger.error("UPNP Error: {0}".format(e))

            time.sleep(self.TIMEOUT)


class UPNP():
    def __init__(self, decoder):
        self._decoder = decoder
        if has_upnp:
            self.upnp = miniupnpc.UPnP()
            self.upnp.discoverdelay = 10

    def addPortForward(self, internal_port, external_port):
        try:
            if has_upnp:
                discover = self.upnp.discover()
                igd = self.upnp.selectigd()
                port_result = self.upnp.addportmapping(external_port, 'TCP', self.upnp.lanaddr, internal_port, 'AlarmDecoder WebApp', '')

                with self._decoder.app.app_context():
                    self._decoder.app.logger.info("Port Forward Attempt: Discovery={0}, IGD={1}, Result={2}".format(discover, igd, port_result))
            else:
                raise ValueError('Missing library: miniupnpc')

        except Exception as e:
            raise

    def removePortForward(self, external_port):
        try:
            if has_upnp:
                discover = self.upnp.discover()
                igd = self.upnp.selectigd()
                port_result = self.upnp.deleteportmapping(external_port, 'TCP')

                with self._decoder.app.app_context():
                    self._decoder.app.logger.info("Port Delete Attempt: Discovery={0}, IGD={1}, Result={2}".format(discover, igd, port_result))
            else:
                raise ValueError('Missing library: miniupnpc')

        except Exception as e:
            raise
