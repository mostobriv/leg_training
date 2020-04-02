#!/usr/bin/env python3
import os
import sys
import requests
from html.parser import HTMLParser
from traceback import format_exc
from mimesis import Generic
import random
import json
import re
from math import gcd
from ast import literal_eval
generic = Generic("en")


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICE_PORT = 5000

SNIPPETS = {
	"python": [
		{
			"content": """def get_flag():
    what_is_it = {}
    return ''.join(map(lambda x: chr(x ^ {}), what_is_it))""",
			"title": "Python paste by {}"
		},
	],
	"c": [
		{
			"content": """char* get_flag()
{{
    char is_it_a_flag_or_not[] = "{}";
    char key[] = "{}";
    char result[33] = {{ 0 }};

    for (int i = 0; i < 32; i++)
    {{
        result[i] = (is_it_a_flag_or_not[i] * key[i]) % 256;
    }}

    return result;
}}""",
			"title": "C paste by {}"
		}
	]
}

C_ALLOW_KEYS = [i for i in range(2, 256) if gcd(i, 256) == 1]


def egcd(a: int, b: int) -> tuple:
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a: int, m: int) -> int:
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


class CSRFGetter(HTMLParser):
	def __init__(self, markup=""):
		super().__init__()
		self.csrf_token = None
		self.feed(markup)

	def handle_starttag(self, tag, attrs):
		if self.csrf_token is None and tag == "input":
			attrs = dict(attrs)
			if attrs.get("id") == "csrf_token":
				self.csrf_token = attrs["value"]


class CodeGetter(HTMLParser):
	def __init__(self, markup=""):
		super().__init__()
		self._recording = None
		self.code = ""
		self.feed(markup)
		self.code = self.code.strip()

	def handle_starttag(self, tag, attrs):
		if self._recording is None and tag == "div":
			attrs = dict(attrs)
			if attrs.get("class") == "highlight":
				self._recording = False
		if tag == "pre" and self._recording == False:
			self._recording = True

	def handle_data(self, data):
		if self._recording == True:
			self.code += data

	def handle_endtag(self, tag):
		if tag == "pre" and self._recording == True:
			self._recording = False
		elif tag == "div" and self._recording == False:
			self._recording = None


def close(code, public=None, private=None):
	if public is not None:
		print(public)
	if private is not None:
		print(private, file=sys.stderr)
	print('Exit with code {}'.format(code), file=sys.stderr)
	exit(code)


def wrong_command(*args):
	close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def generate_paste():
	return "text", ".\n".join(generic.text.text().split(". ")), "Paste by {}".format(generic.person.username())


def generate_flag_paste(flag):
	lang = random.choice(list(SNIPPETS))
	content_title = random.choice(SNIPPETS[lang])
	if lang == "python":
		key = random.getrandbits(8)
		flag_repr = str([ord(letter) ^ key for letter in flag])
		return lang, content_title["content"].format(flag_repr, key), content_title["title"].format(generic.person.username())
	elif lang == "c":
		decrypt_key = random.choices(C_ALLOW_KEYS, k=32)
		encrypt_key = list(map(lambda k: modinv(k, 256), decrypt_key))
		encrypted_flag = map(lambda x, k: (ord(x) * k) % 256, flag, encrypt_key)
		encrypted_flag = "".join(map("\\x{:02x}".format, encrypted_flag))
		decrypt_key = "".join(map("\\x{:02x}".format, decrypt_key))
		return lang, content_title["content"].format(encrypted_flag, decrypt_key), content_title["title"].format(generic.person.username())


def put(*args):
	team_ip, _, flag = args[:3]
	SERVICE_URL = "http://{}:{}".format(team_ip, SERVICE_PORT)
	with requests.Session() as session:
		resp = session.get(SERVICE_URL + "/paste/new")
		csrf_token = CSRFGetter(resp.text).csrf_token
		lang, content, title = generate_flag_paste(flag)
		new_paste_data = {
			"csrf_token": csrf_token,
			"content": content,
			"title": title,
			"lang": lang,
			"submit": "Create New Paste",
			"private": "y"
		}
		resp = session.post(SERVICE_URL + "/paste/new", data=new_paste_data)
		if "Your paste has been created!" not in resp.text:
			close(MUMBLE, "Paste didnt created")
		token = resp.url.split("/")[-1] + ":" + lang
		close(OK, token)


def check(*args):
	team_ip = args[0]
	SERVICE_URL = "http://{}:{}".format(team_ip, SERVICE_PORT)
	# Проверка создания пасты
	with requests.Session() as session:
		resp = session.get(SERVICE_URL + "/paste/new")
		csrf_token = CSRFGetter(resp.text).csrf_token
		lang, content, title = generate_paste()
		new_paste_data = {
			"csrf_token": csrf_token,
			"content": content,
			"title": title,
			"lang": lang,
			"submit": "Create New Paste"
		}
		resp = session.post(SERVICE_URL + "/paste/new", data=new_paste_data)
		if "Your paste has been created!" not in resp.text:
			close(MUMBLE, "Paste didnt created")
		flag_id = resp.url.split("/")[-1]

	# Поиск созданной пасты
	resp = requests.get(SERVICE_URL + "/search", params={"query": title})
	if title not in resp.text:
		close(MUMBLE, "Paste not found through the search")

	# Получение пасты по идентификатору
	resp = requests.get(SERVICE_URL + "/paste/" + flag_id)
	if title not in resp.text:
		close(MUMBLE, "Paste not found by its identifier")

	# Сравнение текста пасты с тем, что отправили
	if CodeGetter(resp.text).code != content:
		close(MUMBLE, "Paste content corrupted")

	close(OK)


def get(*args):
	team_ip, token, flag = args[:3]
	SERVICE_URL = "http://{}:{}".format(team_ip, SERVICE_PORT)
	flag_id, lang = token.split(":")
	resp = requests.get(SERVICE_URL + "/paste/" + flag_id)
	code_snippet = CodeGetter(resp.text).code
	if lang == "python":
		flag_repr = re.search(r"\[[\d, ]+\]", code_snippet)
		if flag_repr is not None:
			flag_repr = json.loads(flag_repr.group())
		else:
			close(CORRUPT, "Encrypted flag not found")
		key = re.search(r"chr\(x \^ (\d+)\)", code_snippet)
		if key is not None:
			key = int(key.group(1))
		else:
			close(CORRUPT, "Key for flag encrypt not found")
		if flag == "".join(chr(x ^ key) for x in flag_repr):
			close(OK)
		else:
			close(CORRUPT, "Decrypted flag doesnt match expected flag")
	elif lang == "c":
		flag_repr = re.search(r"flag_or_not\[\] = (\"[\\x0-9a-f]+\");", code_snippet)
		if flag_repr is not None:
			flag_repr = literal_eval(flag_repr.group(1))
		else:
			close(CORRUPT, "Encrypted flag not found")
		key = re.search(r"key\[\] = (\"[\\x0-9a-f]+\");", code_snippet)
		if key is not None:
			key = literal_eval(key.group(1))
		else:
			close(CORRUPT, "Key for flag decrypt not found")
		if flag == "".join(map(lambda c, k: chr((c*k)%256), map(ord, flag_repr), map(ord, key))):
			close(OK)
		else:
			close(CORRUPT, "Decrypted flag doesnt match expected flag")


def info(*args):
	close(OK, "vulns: 1")


def init(*args):
	close(OK)


ACTIONS = {
	'put': put,
	'check': check,
	'get': get,
	'info': info,
	'init': init
}


def main():
	try:
		ACTIONS.get(sys.argv[1], wrong_command)(*sys.argv[2:])
	except requests.exceptions.ConnectionError:
		close(DOWN)
	except Exception:
		close(CHECKER_ERROR, private="INTERNAL ERROR:\n{}".format(format_exc()))


if __name__ == "__main__":
	main()
