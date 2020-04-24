#!/usr/bin/env python

import requests
import json
import random
import string
import sys


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "restful_pieces"
PORT = 17649


def random_string(N=16, alph=string.lowercase + string.uppercase + string.digits):
    return ''.join([random.choice(alph) for _ in xrange(N)])

def info(*args):
    close(OK, "vulns: 1")


def init(*args):
    close(OK)


def error_arg(*args):
    close(CHECKER_ERROR, private = "Wrong command {}".format(sys.argv[1]))


def close(code, public = "", private = ""):
    exit(code)


def store_post(addr, j):
    if type(j) is dict:
        j = json.dumps(j)
    try:
        h = {'Content-type': 'application/json'}
        return requests.post('http://%s:%d/store' % (addr, PORT), data=j, headers=h)
    except:
        return None

def get_post(addr, j):
    if type(j) is dict:
        j = json.dumps(j)
    try:
        h = {'Content-type': 'application/json'}
        return requests.get('http://%s:%d/get' % (addr, PORT), data=j, headers=h)
    except:
        return None


def check(addr, *args):
    try:
        title, content = random_string(N=32), random_string(128)
        j = {'title': title, 'content': content, 'public': 1}
        resp = store_post(addr, json.dumps(j))
        if resp is None:
            return DOWN 

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE

        resp_json = json.loads(resp.text)
        j = resp_json['data']
        resp = get_post(addr, j)
        if resp is None:
            return DOWN

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE


        if resp_json['data']['title'] != title or resp_json['data']['content'] != content:
            return CORRUPT

        title, content, token = random_string(N=32), random_string(N=128), random_string(N=24)
        j = {'title': title, 'content': content, 'public': 0, "token": token}
        resp = store_post(addr, json.dumps(j))
        if resp is None:
            return DOWN 

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE

        j = resp_json['data']
        j['token'] = token
        resp = get_post(addr, j)
        if resp is None:
            return DOWN

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE

        if resp_json['data']['title'] != title or resp_json['data']['content'] != content:
            return CORRUPT

    except Exception as e:
        sys.stderr.write('[ERROR] %s\n' % e)
        return CHECKER_ERROR

    return OK

    
def put(addr, _token, flag, *args):
    try:
        token = random_string()
        resp = store_post(addr, {'title': random_string(), 'content': flag, 'public': 0, 'token': token})
        if resp is None:
            return DOWN

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE

        if resp_json['status'] != 'success':
            return MUMBLE

        print '%s:%d' % (token, resp_json['data']['post_id'])


    except KeyError:
        return MUMBLE

    except Exception as e:
        sys.stderr.write('Exception: %s' % str(e))
        return CHECKER_ERROR

    return OK

def get(addr, token, flag, *args):
    try:
        token, post_id = token.split(':')
        resp = get_post(addr, {'post_id': post_id, "token": token})
        if resp is None:
            return DOWN

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            return MUMBLE

        if resp_json['status'] != 'success' or resp_json['data']['content'] != flag:
            return CORRUPT

    except KeyError:
        return MUMBLE

    except Exception as e:
        return CHECKER_ERROR

    return OK


COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        exit(COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:]))
    except Exception as ex:
        close(CHECKER_ERROR, private = "INTERNAL ERROR: {}".format(ex))
