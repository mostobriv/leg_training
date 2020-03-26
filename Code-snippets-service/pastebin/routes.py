from flask import render_template, url_for, flash, redirect, request
from pastebin import app, db
from pastebin.forms import PasteForm
from pastebin.models import Paste
from pastebin.functions import *
from sqlalchemy import desc
import uuid

@app.route("/")
@app.route("/home")
def home():
    pastes = Paste.query.filter_by(private="0").order_by(desc(Paste.date_posted))
    return render_template('home.html', pastes=pastes)

@app.route("/paste/new", methods=['GET', 'POST'])
def new_paste():
    form = PasteForm()
    uu_id = uuid.uuid4();
    if form.validate_on_submit():
        paste = Paste(content=form.content.data, title=form.title.data, uu_id=uu_id.hex, private=form.private.data, lang=form.lang.data)
        db.session.add(paste)
        db.session.commit()
        flash('Your paste has been created!', 'success')
        return redirect(url_for('paste', paste_uuid=uu_id.hex))
    return render_template('create_paste.html', title='New Paste',
                           form=form, legend='New Paste')

@app.route("/paste/<paste_uuid>")
def paste(paste_uuid):
    paste = Paste.query.filter_by(uu_id=paste_uuid).first_or_404()
    return render_template('paste.html', paste=paste)

@app.route("/search")
def search():
    if request.args.get('query'):
        try:
            pastes = Paste.query.whooshee_search(request.args.get('query')).order_by(Paste.id.desc()).all()
            return render_template('home.html', pastes=pastes)
        except:
            flash('You should enter at least 3 symbols', 'danger')
    return redirect(url_for('home'))