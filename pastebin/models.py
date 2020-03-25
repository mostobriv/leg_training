from datetime import datetime
from pastebin import db, app, whooshee
from flask_whooshee import Whooshee, AbstractWhoosheer


@whooshee.register_model('title', 'content')
class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    lang = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    uu_id = db.Column(db.Text, nullable=False)
    private = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f"Paste('{self.title}', '{self.date_posted}')"

