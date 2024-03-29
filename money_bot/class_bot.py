import requests as req
from bot_config import time
import datetime


class Tg_bot:
    def __init__(self, token):
        self.token = token
        self.url = f'https://api.telegram.org/bot{self.token}/'

    def get_updates(self):
        method = 'getupdates'
        r = req.get(self.url + method)
        return r.json()

    def get_message(self):
        if not self.connection_chek():
            return None
        data = self.get_updates()
        last_obj = data['result'][-1]

        chat_id = last_obj['message']['chat']['id']
        message_text = last_obj['message']['text']

        message = {'chat_id': chat_id,
                   'text': message_text}
        return message

    def send_message(self, chat_id, text):
        method = 'sendMessage'
        params = {
            "chat_id": chat_id,
            'text': text
        }
        response = req.post(self.url + method, params)
        return response

    def last_messsages_from_me(self, count_messages):
        if not self.connection_chek():
            return
        data = self.get_updates()
        results = data['result']
        last_obj = results[-1]

        chat_id = last_obj['message']['chat']['id']

        count_available_messages = len(results)
        if count_available_messages < count_messages:
            index = -count_available_messages
            message_text = results[index]['message']['text']
            self.send_message(chat_id, f'{count_available_messages} messages ago u texted:\n' + message_text)
        else:
            index = -count_messages
            message_text = results[index]['message']['text']
            self.send_message(chat_id, f'{count_messages} messages ago u texted:\n' + message_text)

    def connection_chek(self):
        method = 'getupdates'
        r = req.get(self.url + method)
        if r.status_code != 200:
            print(f'Error: {r.status_code}, ' + r.json()['description'])
            return False
        return True


class Money_bot(Tg_bot):

    def __init__(self, token):
        super().__init__(token)
        self.money_url = 'http://www.nbrb.by/api/exrates/rates?periodicity=0'

    def get_money(self):
        response = req.get(self.money_url).json()
        usd_price = eur_price = pln_price = 'NOT_FOUND'
        for p in list(response):
            if p["Cur_Abbreviation"] == "USD":
                usd_price = p["Cur_OfficialRate"]
            if p["Cur_Abbreviation"] == "EUR":
                eur_price = p["Cur_OfficialRate"]
            if p["Cur_Abbreviation"] == "PLN":
                pln_price = p["Cur_OfficialRate"]
        return f'Cost of money BYN today - {usd_price} USD, {eur_price} EUR, {pln_price} PLN'

    def record_message_to_file(self):
        with open('messages/message' + ''.join(str(time).split(':')) + '.txt', 'w') as message_file:
            last_user_message = self.get_updates()['result'][-2]['message']['text']
            message_file.write(last_user_message + '\n')
