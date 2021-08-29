import re

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

import list_org_parser
import online_searcher

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaaaa'
APP_NAME = 'GPN SEARCH'
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/tech', methods=['GET', 'POST'])
def tech():
    search_form = TechSearchForm()
    search_results = []

    if search_form.validate_on_submit():
        query = search_form.search_box.data
        # search_results = db_searcher.search_patents(query)
        search_results = online_searcher.get_patents(query)

    return render_template('tech.html', title=APP_NAME, search_form=search_form, results=search_results)


@app.route('/contacts/<name>')
def get_contacts(name):
    print(name)
    names = name.split('<br>')
    infos = []
    for n in names:
        infos.append(f'<b>{n}</b>:<br>{list_org_parser.get_contacts(list_org_parser.get_link(n))}')
    return '<br>'.join(infos).replace('\n', '<br>')


class TechSearchForm(FlaskForm):
    search_box = StringField('', validators=[DataRequired()])
    search_btn = SubmitField('Поиск')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')