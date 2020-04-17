#!/usr/bin/env python3

import random
import sys
import string
from pwn import *


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "keepnotes"
PORT = 9091


def generate_rand(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def auth(io):
    username = generate_rand(25)
    pwd = generate_rand(25)

    try:
        io.sendline("1")
        io.recvuntil("login:")
        io.sendline(username)
        io.recvuntil("password:")
        io.sendline(pwd)

        io.sendline("2")
        io.recvuntil("login:")
        io.sendline(username)
        io.recvuntil("password:")
        io.sendline(pwd)

        check_auth = io.readline().decode().strip()
        if check_auth != "!_____SUCCESSFULLY_____!":
            close(MUMBLE, private = "Failed to authorize")

        return username, pwd

    except EOFError:
        close(DOWN, private = "EOFError while recv smth")
    except PwnlibException as e:
        close(DOWN, private = "Failed to connect: {}".format(e))


def put(*args):
    team_ip, _, flag = args[:3]

    try:
        io = remote(team_ip, PORT, level = 60)
        io.recvuntil("|\n-----------------------------------------------------------\n")
        _, _ = auth(io)
        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline("3")
        io.readline()
        io.sendline(flag)
        token = io.recvline().decode().split()[-1]
        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline("4")
        io.recvline()
        io.sendline(token)
        check_token = io.recvline().decode().strip()
        if check_token == "there is no such token, sorry":
            close(MUMBLE, private = "Failed to put flag")
        close(OK, token)

    except EOFError:
        close(DOWN, private = "EOFError while recv smth")
    except PwnlibException as e:
        close(DOWN, private = "Failed to connect: {}".format(e))


def check_output(io, command, expected_str, errorname):
        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline(str(command))
        check = io.readline().decode().strip()
        if check != expected_str:
            close(MUMBLE, private = errorname)


def check(*args):
    team_ip = args[0]

    try:
        io = remote(team_ip, PORT, level = 60)

        # try to do sth without auth
        check_output(io, 3, "you need login first of all", "Unauthorized access")
        check_output(io, 4, "you need login first of all", "Unauthorized access")
        check_output(io, 5, "you are not admin", "Unauthorized access")

        _, _ = auth(io)

        # try see all secrets with auth
        check_output(io, 5, "you are not admin", "Unauthorized access")

        # put note
        note = generate_rand(32)

        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline("3")
        io.readline()
        io.sendline(note)

        # take note
        token = io.recvline().decode().split()[-1]

        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline("4")
        io.recvline()
        io.sendline(token)
        check_token = io.recvline().decode().strip()
        if check_token == "there is no such token, sorry":
            close(MUMBLE, private = "Failed to put note")

        close(OK)

    except EOFError:
        close(DOWN, private = "EOFError while recv smth")
    except PwnlibException as e:
        close(DOWN, private = "Failed to connect: {}".format(e))


def get(*args):
    team_ip, token, flag = args[:3]

    try:
        io = remote(team_ip, PORT, level = 60)
        io.recvuntil("|\n-----------------------------------------------------------\n")
        _, _ = auth(io)
        io.recvuntil("|\n-----------------------------------------------------------\n")
        io.sendline("4")
        io.recvline()
        io.sendline(token)
        old_flag = io.recvline().decode().split()[-1]
        if old_flag != flag:
            close(CORRUPT, private = "Failed to find old flag")
        close(OK)

    except EOFError:
        close(DOWN, private = "EOFError while recv smth")
    except PwnlibException as e:
        close(DOWN, private = "Failed to connect: {}".format(e))


def info(*args):
    close(OK, "vulns: 1")


def init(*args):
    close(OK)


def error_arg(*args):
    close(CHECKER_ERROR, private = "Wrong command {}".format(sys.argv[1]))


def close(code, public = "", private = ""):
    if public:
        print(public)
    if private:
        print(private, file = sys.stderr)
    print('Exit with code {}'.format(code), file = sys.stderr)
    exit(code)


COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private = "INTERNAL ERROR: {}".format(ex))
