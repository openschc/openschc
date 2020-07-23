# coding: utf-8
class LNS:
    "LNS class, contains all parameters required to communicate with a given LNS"

    def __init__(self, device_id, mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_secured=True):
        self._mqtt_url = mqtt_url
        self._mqtt_port = mqtt_port
        self._mqtt_username = mqtt_username
        self._mqtt_password = mqtt_password
        self._device_id = device_id
        self._mqtt_secured = mqtt_secured

    @property
    def mqtt_username(self):
        return self._mqtt_username

    @mqtt_username.setter
    def mqtt_username(self, username):
        self._mqtt_username = username

    @property
    def mqtt_password(self):
        return self._mqtt_password

    @mqtt_password.setter
    def mqtt_password(self, password):
        self._mqtt_password = password

    @property
    def mqtt_url(self):
        return self._mqtt_url

    @mqtt_url.setter
    def mqtt_url(self, url):
        self._mqtt_url = url

    @property
    def mqtt_port(self):
        return self._mqtt_port

    @mqtt_port.setter
    def mqtt_port(self, port):
        self._mqtt_port = port

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, device_id):
        self._device_id = device_id

    @property
    def mqtt_secured(self):
        return self._mqtt_secured

    @mqtt_secured.setter
    def mqtt_secured(self, secured):
        self._mqtt_secured = secured
    
    @property
    def mqtt_topic_uplink(self):
        raise NotImplementedError