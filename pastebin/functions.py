import jinja2_highlight
from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter
from pastebin import app


@app.context_processor
def utility_processor():
    def highlighter(code, lang):
        return highlight(code, get_lexer_by_name(lang),  HtmlFormatter(linenos=True))
    return dict(highlighter=highlighter)