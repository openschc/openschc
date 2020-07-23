# coding: utf-8
from LNS import LNS
import json

class LNS_TTN_V2(LNS):
   def __init__(self, device_id, mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_secured=True):
      super().__init__(device_id, mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_secured)

   @property
   def mqtt_topic_uplink(self):
      return f"+/devices/{self.device_id}/up"

   @staticmethod
   def get_payload(msg_queue, payload, f_port):
      try:
         payload = json.loads(payload.decode("utf-8"))
         # print(msg.topic, pformat(payload))
         if payload["port"] != f_port:
               return
         payload = base64.b64decode(payload["payload_raw"])
         print("UPLINK - Payload:", payload.hex())
         print(f"UPLINK - Payload length: {len(payload)}")
         msg_queue.put(payload)
      except Exception as e:
         print(str(e))