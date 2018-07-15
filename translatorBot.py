import requests
import json
import re
from function import TelegramBotAction


class TranslatorBot(object):
    def __init__(self):
        self.keys = self._readAPIKey()
        self.action = TelegramBotAction(self.keys['gege'])

    def _readLastUpdate(self, source_lang, target_lang):
        try:
            with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'r') as f:
                number = f.read()

            return int(number)

        except:
            self._writeUpdate(source_lang, target_lang, 0)
            return 0

    def _readAPIKey(self):
        with open('apikey.json', 'r') as f:
            keys = json.load(f)
        return keys

    def _writeUpdate(self, source_lang, target_lang, number):
        with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'w') as f:
            f.write(str(number))

    def _crawlUpdate(self, api_endpoint, offset):
        payload = {"offset": offset}
        resp = requests.post(api_endpoint, data=payload)
        data = resp.json()
        return data['result']

    def _get_lang_id(self, lang):
        lang_table = {
                "ko": 1
              , "en": 2
              , "zh": 4
              , "th": 6
              , "ja": 8
              , "es": 9
              , "pt": 10
              , "vi": 11
              , "de": 12
              , "fr": 13
                }
        return lang_table.get(lang)

    def _get_mail(self):
        with open('getMail.txt', 'r') as f:
            data_raw = f.read()
            data = data_raw.split(',')

        return data[0].strip(), data[1].strip()

    def _translate(self, source_lang, target_lang, sentence, order_user, memo):
        endpoint = "http://translator.ciceron.me:5000/api/v2/internal/translate"
        payload = {
                    "source_lang": source_lang
                  , "target_lang": target_lang
                  , "sentence": sentence
                  , "tag": "telegram"
                  , "order_user": order_user
                  , "media": "telegram"
                  , "where_contributed": "telegram"
                  , "memo": memo
                }
        headers = {"Authorization": self.keys['apikey']}
        key, value = self._get_mail()
        payload[key] = value
        try:
            resp = requests.post(endpoint, data=payload, headers=headers, timeout=10, verify=False)
            data = resp.json() if resp.status_code == 200 else {"ciceron":"Not enough servers. Investment is required.", 'google':""}

        except:
            data = {"ciceron":"Not enough servers. Investment is required.", 'google':""}

        result_ciceron = data.get('ciceron')
        result_google = data.get('google')
        result_human = data.get('human')
        if source_lang in ["en", "ko"] and target_lang in ["en", "ko"]:
            message  = "LangChain:\n*{}*\n\n".format(result_ciceron)
            if result_human is not None:
                message += "Human guided:\n*{}*\n\n".format(result_human)
            message += "Google:\n*{}*\n\n".format(result_google)
            message += "Powered by LangChain"

            message_usage  = "Usage: !'Source language''Target language' 'Sentence'\n"
            message_usage += "Ex) !enko Hello?\n\n"
            message_usage += "Korean - ko / English - en / Japanese - ja\nChinese - zh / Thai - th / Spanish - es\nPortuguese - pt / Vietnamese - vi / German - de\nFrench - fr / Russian - ru / Indonesian - in\n\n"
            message_usage += "You can train @langchainbot by @LangChainTrainerbot and get LangChain point!"

        else:
            message = "Google:\n*{}*\n\n".format(result_google)
            if result_human is not None:
                message += "Human guided:\n*{}*\n\n".format(result_human)
            message += "Powered by LangChain"

            message_usage  = "Usage: !'Source language''Target language' 'Sentence'\n"
            message_usage += "Ex) !enko Hello?\n\n"
            message_usage += "Korean - ko / English - en / Japanese - ja\nChinese - zh / Thai - th / Spanish - es\nPortuguese - pt / Vietnamese - vi / German - de\nFrench - fr / Russian - ru / Indonesian - in\n\n"
            message_usage += "You can train @langchainbot by @LangChainTrainerbot and get LangChain point!"


        return message, message_usage

    def _sendMessage(self, api_endpoint, chat_id, message_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "reply_to_message_id": message_id
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

        return resp.json()

    def _editMessage(self, api_endpoint, chat_id, message_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "message_id": message_id
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

        return resp.json()

    def _sendNormalMessage(self, api_endpoint, chat_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "parse_mode": "Markdown"
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

    def _main(self, source_lang, target_lang, apiKey, wakeup_key):
        apiEndpoint_update = "https://api.telegram.org/bot{}/getUpdates".format(apiKey)
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(apiKey)

        lastnumber = self._readLastUpdate(source_lang, target_lang)
        res = self._crawlUpdate(apiEndpoint_update, lastnumber+1)

        update_id = lastnumber
        for item in res:
            if item['update_id'] < lastnumber:
                continue

            update_id = max(update_id, item['update_id'])
            whole_message = item.get('message')
            if whole_message is None:
                continue

            chat_id = item['message']['chat']['id']
            message_id = item['message']['message_id']
            text_before = item['message'].get('text')
            user_name = item['message'].get('from').get('username')
            chat_type = item['message']['chat']['type']
            group_title = item['message']['chat'].get('title')
            if text_before is None:
                continue
            else:
                text_before = text_before.strip()

            if text_before.startswith(wakeup_key):
                text_before = text_before.replace(wakeup_key, '').strip()
                print(text_before)
                message, message_usage = self._translate(source_lang, target_lang, text_before, user_name, "Telegram:{}|{}|{}".format(user_name, chat_type, group_title))
                print(message)
                self._sendMessage(apiEndpoint_send, chat_id, message_id, message)
                self._sendNormalMessage(apiEndpoint_send, chat_id, message_usage)

        self._writeUpdate(source_lang, target_lang, update_id)

    def _generalMain(self, apiKey, wakeup_key):
        apiEndpoint_update = "https://api.telegram.org/bot{}/getUpdates".format(apiKey)
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(apiKey)
        apiEndpoint_edit = "https://api.telegram.org/bot{}/editMessageText".format(apiKey)

        lastnumber = self._readLastUpdate("ge", "ge")
        res = self._crawlUpdate(apiEndpoint_update, lastnumber+1)

        update_id = lastnumber
        source_lang = ""
        target_lang = ""

        for item in res:
            if item['update_id'] < lastnumber:
                continue

            update_id = max(update_id, item['update_id'])
            whole_message = item.get('message')
            if whole_message is None:
                continue

            chat_id = item['message']['chat']['id']
            message_id = item['message']['message_id']
            text_before = item['message'].get('text')
            user_name = item['message'].get('from').get('username')
            chat_type = item['message']['chat']['type']
            group_title = item['message']['chat'].get('title')
            id_external = item['message']['from'].get('id')

            user_info = self.action._getId(id_external, chat_id=chat_id, text_id=user_name)
            
            if text_before is None:
                continue
            else:
                text_before = text_before.strip()

            if text_before == '/start' or text_before == '/help':
                message_usage  = "*Welcome to LangChain Translation Bot!*\n"
                message_usage += "Use translator without external translation app!\n\n"
                message_usage += "Usage: !'Source language''Target language' 'Sentence'\n"
                message_usage += "Ex) !enko Hello?\n\n"
                message_usage += "Korean - ko / English - en / Japanese - ja\nChinese - zh / Thai - th / Spanish - es\nPortuguese - pt / Vietnamese - vi / German - de\nFrench - fr / Russian - ru / Indonesian - in\n\n"
                message_usage += "You can train @langchainbot by @LangChainTrainerbot and get LangChain point!"
                self._sendNormalMessage(apiEndpoint_send, chat_id, message_usage)

            elif text_before.startswith(wakeup_key):
                lang_obj = re.search(r'\A!([a-z]{2})([a-z]{2})', text_before)
                if lang_obj == None:
                    continue

                ret = self._sendMessage(apiEndpoint_send, chat_id, message_id, "Translating...")

                language_pair = lang_obj.group(0)
                source_lang = lang_obj.group(1)
                target_lang = lang_obj.group(2)
                new_chat_id = ret['result']['chat']['id']
                new_message_id = ret['result']['message_id']

                text_before = text_before.replace(language_pair, '').strip()
                print(text_before)
                message, message_usage = self._translate(source_lang, target_lang, text_before, user_name, "Telegram:{}|{}|{}".format(user_name, chat_type, group_title))
                print(message)
                self._editMessage(apiEndpoint_edit, new_chat_id, new_message_id, message)
                self._sendNormalMessage(apiEndpoint_send, chat_id, message_usage)

        self._writeUpdate("ge", "ge", update_id)

    def koEnTranslation(self):
        self._main('ko', 'en', self.keys['koen'], '!koen')

    def enKoTranslation(self):
        self._main('en', 'ko', self.keys['enko'], '!enko')

    def generalTranslation(self):
        self._generalMain(self.keys['gege'], '!')


if __name__ == "__main__":
    translator = TranslatorBot()
    translator.koEnTranslation()
