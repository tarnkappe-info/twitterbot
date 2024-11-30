#!/usr/bin/env python
import json
import requests
import websocket
import _thread
import time
import rel

def writeinfile(data, filepath):
    data = str(data)
    with open(filepath) as file:
        if data not in file.read():
            # Open a file with access mode 'a'
            file_object = open(filepath, 'a')
            # Append 'hello' at the end of file
            file_object.write(data + '\n')
            # Close the file
            file_object.close()
            return True
        else:
            return False


mynumber = "+4917677918637"

def on_message(ws, single_message):
    print(single_message)
    single_message = json.loads(single_message)
    if single_message['envelope'].get('dataMessage'):
        if not single_message['envelope']['dataMessage'].get("groupInfo"):
            if single_message['envelope']['dataMessage']['message'].lower() == 'start':
                if single_message['envelope'].get('sourceNumber'):
                    if writeinfile(single_message['envelope']['sourceNumber'], "/root/Signal/rss/numbers.txt"):
                        requests.post('http://127.0.0.1:8120/v2/send/', timeout=10, json={"message": "Vielen Dank! Sie erhalten ab sofort die neusten Nachrichten.", "number": mynumber, "recipients": [ single_message['envelope']['sourceNumber'] ]})
                        """""else:
                    if writeinfile(single_message['envelope']['sourceName'], "/root/Signal/rss/usernames.txt"):
                        requests.post('http://127.0.0.1:8120/v2/send/', timeout=10,
                                      json={"message": "Vielen Dank! Sie erhalten ab sofort die neusten Nachrichten.",
                                            "number": mynumber, "recipients": [single_message['envelope']['sourceName']]})"""""
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


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp('ws://127.0.0.1:8120/v1/receive/'+mynumber+'?ignore_stories=true&ignore_attachments=true&timeout=5&send_read_receipts=true',
                              on_message=on_message)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()