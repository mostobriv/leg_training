from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class PasteForm(FlaskForm):
    title = StringField('Paste Name / Title:', validators=[DataRequired()], default='untitled')
    content = TextAreaField('New Paste', validators=[DataRequired()])
    lang = SelectField('Syntax Highlighting:', choices=[
        ('text', 'None'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('csharp', 'C#'),
        ('php', 'PHP'),
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('swift', 'Swift'),
        ('ruby', 'Ruby'),
        ('go', 'Go'),
        ('scala', 'Scala'),
        ('c', 'C'),
        ('sql', 'SQL'),
        ('perl', 'Perl'),
        ('html', 'Html'),
        ('css', 'Css')])
    private = BooleanField('Private')
    submit = SubmitField('Create New Paste')
