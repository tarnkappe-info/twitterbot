#!/usr/bin/env python
import json
import requests
import websocket
import _thread
import time
import rel

mynumber = "+4917677918637"

ids = requests.get('http://127.0.0.1:8120/v1/identities/'+mynumber, timeout=600,)
for i in list(ids.json()):
    if len(i["number"]) > 0 and i["status"] == "UNTRUSTED":
        requests.put('http://127.0.0.1:8120/v1/identities/+4917677918637/trust/' + str(i["number"]), timeout=600,json={"trust_all_known_keys": True})
        time.sleep(0.2)