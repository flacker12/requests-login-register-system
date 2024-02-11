from flask import Flask,render_template, request, session, redirect, url_for
import pymysql
import pymysql.cursors
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = '12345'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        passwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (name, email, password, roleId) VALUES(%s, %s, %s, 0);', (username, email, passwd))
        mysql.connection.commit()
        cur.close()

        return 'success'
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        passwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE name=%s AND password=%s', (username, passwd))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = username
            session['roleId'] = record[4]
            session['id'] = record[0]
            return redirect(url_for('index'))
        else:
            return 'incorrect'
    return render_template('login.html')


@app.route('/home/')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], roleid=session['roleId'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



from flask import Flask, render_template, redirect
from flask_peewee.db import SqliteDatabase
import peewee
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

# Инициализация базы данных
db = SqliteDatabase('database.db')


# Определение модели данных
class Request(peewee.Model):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    email = peewee.CharField()
    subject = peewee.CharField()
    buildingType = peewee.CharField()
    message = peewee.CharField()
    status = peewee.CharField()

    class Meta:
        database = db



# db.create_tables([Request])


# Определение формы для создания заявок
class RequestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    buildingType = StringField('buildingType', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RequestChangeStatusForm(FlaskForm):
    status = SelectField(
        "Новый статус",
        choices=[
            ("completed", "Выполнено"),
            ("InProgress", "В процессе"),
            ("Waitingforchange", "Ожидание сдачи"),
            ("overdue", "Просрочено")
        ],
        validators=[]
    )
class RequestChangeStatusMaster(FlaskForm):
    statusmaster = SelectField(
        "Новый статус",
        choices=[
            ("InProgress", "В процессе"),
            ("Waitingforchange", "Ожидание сдачи"),
        ],
        validators=[]
    )
    submit = SubmitField('Submit')




# Путь для создания заявки
@app.route('/request/', methods=['GET', 'POST'])
def create_request():
    if 'loggedin' in session:
        form = RequestForm()
        if form.validate_on_submit():
            Request.create(
                
                name=form.name.data,
                email=form.email.data,
                subject=form.subject.data,
                buildingType=form.buildingType.data,
                message=form.message.data,
                status='new'
            )
            return redirect('/success')
        return render_template('request.html', form=form)
    return redirect(url_for('login'))




@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/request/<int:request_id>/change_status', methods=['POST', 'GET'])
def change_status(request_id):
    form = RequestChangeStatusForm()
    if session['loggedin']:
        if session['roleId'] == 1:
            if (form.validate_on_submit()):
                _request: Request = Request.get_by_id(request_id)

                status = form.status.data
                _request.status = status
                _request.save()

                return redirect('/success')

            return render_template('change_status.html', form=form)
    return redirect(url_for('home'))

@app.route('/requestspost/', methods=["GET"])
def requests():
    _requests = Request.select()
    if session['loggedin']:
        if session['roleId'] == 1:
            return render_template('requests.html', requests=_requests, id = session['id'])
    return redirect(url_for('home'))

@app.route('/requestcastomer/', methods=["GET"])
def requestcastomer():
    _requests = Request.select()
    if session['loggedin']:
        if session['roleId'] == 0:
            return render_template('requestcastomer.html', requests=_requests)
    return redirect(url_for('login'))


@app.route('/requestmaster/', methods=["GET"])
def requestmaster():
    _requests = Request.select()
    if session['loggedin']:
        if session['roleId'] == 2:
            return render_template('requestmaster.html', requests=_requests)
    return redirect(url_for('home'))



@app.route('/request/<int:request_id>/change_statusmaster', methods=['POST', 'GET'])
def change_statusmaster(request_id):
    form = RequestChangeStatusMaster()
    if session['loggedin']:
        if session['roleId'] == 2:
            if (form.validate_on_submit()):
                _request: Request = Request.get_by_id(request_id)

                statusmaster = form.statusmaster.data
                _request.status = statusmaster
                _request.save()

                return redirect('/success')

            return render_template('change_statusmaster.html', form=form)
    return redirect(url_for('home'))


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')


@app.route('/lic/')
def lic():
    return render_template('lic.html')


if(__name__ == '__main__'):
    try:
        db.create_tables([Request])
    except:pass
    
    app.run(debug=True)