# Vulnerabilities

### No filtering

В функционале поиска по сниппетам отсутствует фильтрация по публичным записям.

```python
@app.route("/search")
def search():
    if request.args.get('query'):
        try:
            pastes = Paste.query.whooshee_search(request.args.get('query')).order_by(Paste.id.desc()).all()
            return render_template('home.html', pastes=pastes)
        except:
            flash('You should enter at least 3 symbols', 'danger')
    return redirect(url_for('home'))
 ```
 
 [sploit](code_snippets.py)
