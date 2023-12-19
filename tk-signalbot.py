#!/usr/bin/env python
import json
import requests

mynumber = "+4917677918637"

request_messages = requests.get('http://127.0.0.1:8120/v1/receive/'+mynumber+'?ignore_stories=true&ignore_attachments=true', timeout=40)

for single_message in request_messages.json():
    if single_message['envelope'].get('dataMessage'):
        if single_message['envelope']['dataMessage']['message'].lower() == 'start':
            with open("/root/Signal/rss/numbers.txt") as file:
                if single_message['envelope']['sourceNumber'] not in file.read():
                    # Open a file with access mode 'a'
                    file_object = open('/root/Signal/rss/numbers.txt', 'a')
                    # Append 'hello' at the end of file
                    file_object.write(request_messages.json()[0]['envelope']['sourceNumber'] + '\n')
                    # Close the file
                    file_object.close()
                    requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Vielen Dank! Sie erhalten ab sofort die neusten Nachrichten.", "number": mynumber, "recipients": [ single_message['envelope']['sourceNumber'] ]})
        elif single_message['envelope']['dataMessage']['message'].lower() == 'stop':
            newfile = []
            with open("/root/Signal/rss/numbers.txt") as file:
                for line in file:
                    if line.rstrip() == single_message['envelope']['sourceNumber']:
                        requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Sie erhalten ab sofort keine Nachrichten mehr.", "number": mynumber, "recipients": [ single_message['envelope']['sourceNumber'] ]})
                    else:
                        newfile.append(line)

            file_object = open('/root/Signal/rss/numbers.txt', 'w')
            file_object.writelines(newfile)
            file_object.close()
        else:
            requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Antworten Sie \"Start\" um die neusten Nachrichten zu erhalten.\nZum beenden, antworten Sie einfach \"Stop\".", "number": mynumber, "recipients": [ single_message['envelope']['sourceNumber'] ]})