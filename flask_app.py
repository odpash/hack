import re

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, Form
from wtforms.validators import DataRequired

import list_org_parser
import online_searcher

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaaaa'
APP_NAME = 'GPN SEARCH'
bootstrap = Bootstrap(app)


class Result:
    def __init__(self, title, description):
        self.title = title
        self.description = description


test_results = [
    Result(f'Company {i}', f'Description {i}') for i in range(1, 10)
]


# @app.route('/companies', methods=['GET', 'POST'])
# def companies():
#     search_form = CompanySearchForm()
#     search_results = []
#
#     if search_form.validate_on_submit():
#         query = search_form.search_box.data
#         only_active = search_form.search_only_active.data
#
#         # search_results = db_searcher.search(query, only_active=only_active)
#
#     return render_template('companies.html', title=APP_NAME, search_form=search_form, results=search_results)


@app.route('/', methods=['GET', 'POST'])
@app.route('/tech', methods=['GET', 'POST'])
def tech():
    search_form = TechSearchForm()
    search_results = []

    if search_form.validate_on_submit():
        query = search_form.search_box.data
        # search_results = db_searcher.search_patents(query)
        search_results = online_searcher.get_patents(query)

    return render_template('tech.html', title=APP_NAME, search_form=search_form, results=search_results, contacts='')


@app.route('/contacts/<name>')
def get_contacts(name):
    print(name)
    name = re.sub(r'<.*?>', '', name)
    print(name)
    names = name.split('<br>')
    infos = []
    for n in names:
        infos.append(f'<b>{n}</b>:<br>{list_org_parser.get_contacts(list_org_parser.get_link(n))}')
    return '<br>'.join(infos).replace('\n', '<br>')


select = lambda x: (x, x)

# categories = list(map(select, ['Не выбрано'] + db_searcher.categories))
# classes = list(map(select, ['Не выбрано'] + db_searcher.classes))
# subclasses = list(map(select, ['Не выбрано'] + db_searcher.subclasses))
levels = list(map(select, ['Не выбрано', 'Низкий', 'Средний', 'Высокий']))


class IntegerRangeForm(Form):
    box_from = IntegerField('От')
    box_to = IntegerField('До')

    def validate(self, extra_validators=None):
        return True


class CompanySearchForm(FlaskForm):
    search_box = StringField('', validators=[DataRequired()])
    search_only_active = BooleanField('Только действующие', default=True)
    # search_category = SelectField('Категория', coerce=str, choices=categories)
    # search_class = SelectField('Класс', coerce=str, choices=classes)
    # search_subclass = SelectField('Подкласс', coerce=str, choices=subclasses)
    #
    # search_registration = FormField(IntegerRangeForm, 'Год регистрации')
    # search_capital = FormField(IntegerRangeForm, 'Уставной капитал (тыс. руб)')
    #
    # search_science = SelectField('Наукоемкость', coerce=str, choices=levels)
    # search_expenses = SelectField('Расходы на НИОКР', coerce=str, choices=levels)
    # search_investment = SelectField('Величина капвложений', coerce=str, choices=levels)
    # search_fund = SelectField('Фондовооруженность', coerce=str, choices=levels)

    search_btn = SubmitField('Поиск')


class TechSearchForm(FlaskForm):
    search_box = StringField('', validators=[DataRequired()])
    search_btn = SubmitField('Поиск')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')