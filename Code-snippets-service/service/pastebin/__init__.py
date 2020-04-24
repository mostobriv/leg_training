from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee, AbstractWhoosheer

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
whooshee = Whooshee(app)

from pastebin import routes

