import requests
import json


class TranslatorBot(object):
    def _readLastUpdate(self, source_lang, target_lang):
        try:
            with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'r') as f:
                number = f.read()

            return int(number)

        except:
            self._writeUpdate(source_lang, target_lang, 0)
            return 0

    def _writeUpdate(self, source_lang, target_lang, number):
        with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'w') as f:
            f.write(str(number))

    def _crawlUpdate(self, api_endpoint, offset):
        payload = {"offset": offset}
        resp = requests.post(api_endpoint, data=payload)
        data = resp.json()
        return data['result']

    def _get_lang_id(self, lang):
        if lang == "ko":
            return 1
        elif lang == "en":
            return 2

    def _get_mail(self):
        with open('getMail.txt', 'r') as f:
            data_raw = f.read()
            data = data_raw.split(',')

        return data[0].strip(), data[1].strip()

    def _translate(self, source_lang, target_lang, sentence):
        endpoint = "https://translator.ciceron.me/translate"
        source_lang_id = self._get_lang_id(source_lang)
        target_lang_id = self._get_lang_id(target_lang)
        payload = {
                    "source_lang_id": source_lang_id
                  , "target_lang_id": target_lang_id
                  , "sentence": sentence
                  , "where": "api"
                }
        key, value = self._get_mail()
        payload[key] = value
        resp = requests.post(endpoint, data=payload, timeout=10, verify=False)
        data = resp.json() if resp.status_code == 200 else {}

        result_ciceron = data.get('ciceron')
        result_google = data.get('google')
        message = "LangChain:\n{}\n\nGoogle:\n{}".format(result_ciceron, result_google)

        return message

    def _sendMessage(self, api_endpoint, chat_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                  }
        requests.post(api_endpoint, data=payload, timeout=5)

    def koEnTranslation(self):
        source_lang = 'ko'
        target_lang = 'en'
        apiEndpoint_update = "https://api.telegram.org/bot575363781:AAGCIxEWupZhjlqBJwPvD6eM_Lin3jXdFnE/getUpdates"
        apiEndpoint_send = "https://api.telegram.org/bot575363781:AAGCIxEWupZhjlqBJwPvD6eM_Lin3jXdFnE/sendMessage"

        lastnumber = self._readLastUpdate(source_lang, target_lang)
        res = self._crawlUpdate(apiEndpoint_update, lastnumber + 1)

        update_id = lastnumber
        for item in res:
            if item['update_id'] < lastnumber:
                continue

            update_id = max(update_id, item['update_id'])
            chat_id = item['message']['chat']['id']
            text_before = item['message']['text']
            print(text_before)
            message = self._translate(source_lang, target_lang, text_before)
            print(message)
            self._sendMessage(apiEndpoint_send, chat_id, message)

        self._writeUpdate(source_lang, target_lang, update_id)


if __name__ == "__main__":
    translator = TranslatorBot()
    translator.koEnTranslation()
