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
generic = Generic("en")


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICE_PORT = 5000

SNIPPETS = {
	"python": [
		{
			"content": """def get_flag():
    what_is_it = {}
    return ''.join(map(lambda x: chr(x ^ {}), what_is_it))""",
			"title": "Paste by {}"
		},
	],
}


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
			self.code = self.code.strip()


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
	key = random.getrandbits(8)
	flag_repr = str([ord(letter) ^ key for letter in flag])
	return lang, content_title["content"].format(flag_repr, key), content_title["title"].format(generic.person.username())


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
		flag_id = resp.url.split("/")[-1]
		close(OK, flag_id)


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
	resp = requests.get(SERVICE_URL, params={"query": title})
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
	resp = requests.get(SERVICE_URL + "/paste/" + token)
	code_snippet = CodeGetter(resp.text).code
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
		close("OK")
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
