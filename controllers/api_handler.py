import requests
import logging
from time import sleep
message_sent = []
def send_messages(tokens, sms_setting):
    sleep(1)
    text_to_next = sms_setting.text_to_next
    text = sms_setting.text
    phone_numbers = [token.phone_number for token in tokens]
    for i in range(text_to_next):
        try:
            if phone_numbers[i] in message_sent:
                continue
            else:
                #form_data = dict(To =phone_numbers[i], Message = text)
                #req = requests.post("http://192.168.137.137:1688/services/api/messaging/", data = form_data)
                message_sent.append(phone_numbers[i])
        except Exception as exp:
            logging.critical(exp)