# all the imports
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,\
abort,render_template,flash

#configuration
DATABASE = r'D:\YUNIO\pythonWorkspace\temp\flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTING',silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
from contextlib import closing
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def show_entries():
    '''Show all articles'''
    cur = g.db.execute('select title,text from entries order by id desc')
    entries = [dict(title=row[0],text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html',entries=entries)

@app.route('/add',methods=['POST'])
def add_entry():
    '''add an article'''
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title,text) values (?,?)',[request.form['title'],request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
@app.route('/login/',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html',error=error)
@app.route('/logout/')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
if __name__ == '__main__':
    app.run()