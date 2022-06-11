#!/usr/bin/env python
import json
import requests

request_messages = requests.get('http://127.0.0.1:8120/v1/receive/+4915156859153', timeout=40)

for single_message in request_messages.json():
    if single_message['envelope'].get('dataMessage'):
        if single_message['envelope']['dataMessage']['message'] == 'Start' or single_message['envelope']['dataMessage']['message'] == 'start':
            requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Damit wir Sie über die neusten Nachrichten informieren können, müssen wir Ihre Telefonnummer auf einem Server in deutschland speichern.\nBitte bestätigen Sie mit der Nachricht \"Akzeptieren\".", "number": "+4915156859153", "recipients": [ single_message['envelope']['sourceNumber'] ]})
        elif single_message['envelope']['dataMessage']['message'] == 'Akzeptieren':
            with open("/root/Signal/rss/numbers.txt") as file:
                if single_message['envelope']['sourceNumber'] not in file.read():
                    # Open a file with access mode 'a'
                    file_object = open('/root/Signal/rss/numbers.txt', 'a')
                    # Append 'hello' at the end of file
                    file_object.write(request_messages.json()[0]['envelope']['sourceNumber'] + '\n')
                    # Close the file
                    file_object.close()
                    requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Vielen Dank! Sie erhalten ab sofort die neusten Nachrichten.", "number": "+4915156859153", "recipients": [ single_message['envelope']['sourceNumber'] ]})
        elif single_message['envelope']['dataMessage']['message'] == 'Stop':
            newfile = []
            with open("/root/Signal/rss/numbers.txt") as file:
                for line in file:
                    if line.rstrip() == single_message['envelope']['sourceNumber']:
                        requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Sie erhalten ab sofort keine Nachrichten mehr.", "number": "+4915156859153", "recipients": [ single_message['envelope']['sourceNumber'] ]})
                    else:
                        newfile.append(line)

            file_object = open('/root/Signal/rss/numbers.txt', 'w')
            file_object.writelines(newfile)
            file_object.close()
        else:
            requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Antworten Sie \"Start\" um die neusten Nachrichten zu erhalten.\nZum beenden, antworten Sie einfach \"Stop\".", "number": "+4915156859153", "recipients": [ single_message['envelope']['sourceNumber'] ]})