# coding: utf-8
from LNS import LNS

class LNS_TTN_V2(LNS):
   def __init__(self, device_id, mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_secured=True):
      super().__init__(device_id, mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_secured)

   @property
   def mqtt_topic_uplink(self):
      return f"+/devices/{self.device_id}/up"