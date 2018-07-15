import requests
import json


class TelegramBotAction(object):
    def __init__(self, api_key):
        self.domain = "http://localhost:5000"
        self.api_key = api_key

    def _sendNormalMessage(self, chat_id, message):
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(self.api_key)
        payload = { 
                      "chat_id": chat_id
                    , "text": message
                    , "parse_mode": "Markdown"
                  }   
        for _ in range(100):
            try:
                resp = requests.post(apiEndpoint_send, data=payload, timeout=5)
            except:
                continue

            if resp.status_code == 200:
                break

    def _getId(self, id_external, chat_id=None, text_id=None):
        payloads = {
                "media": "telegram"
              , "text_id": text_id
              , "id_external": id_external
                }
        if chat_id != None:
            payloads['chat_id'] = chat_id
    
        try:
            resp = requests.post("{}/api/v1/getId".format(self.domain), data=payloads, timeout=5)
        except:
            message_fail = "There seems a trouble to execute it. Please try again!"
            self._sendNormalMessage(chat_id, message_fail)
            return

        ret = resp.json()
        return ret
    
