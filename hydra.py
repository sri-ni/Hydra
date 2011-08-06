"""
	Hydra(te)
	~~~~~~~~~
	
	A web application to log your hydration routine.
	
	:copyright: (c) 2011 by Thirumalaa Srinivas.
	:license: BSD, see LICENSE for more details.
"""

# All the imports
from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from time import gmtime, strftime, localtime

# Configuration
DATABASE = '/tmp/hydra.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'coderishi'
PASSWORD = 'coderishi'

# Create our little application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('HYDRA_SETTINGS', silent=True)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()
		
@app.before_request
def before_request():
	"""Make sure we are connected to database on each request"""
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	"""Closes the database again at the end of each request"""
	g.db.close()

def count_userbase():
	count = g.db.execute('select COUNT(username) from accounts')
	usercount = count.fetchall()
	return usercount[0]
	
@app.route('/')
def home():
	for usercount in count_userbase(): pass
	return render_template('home.html', usercount=usercount)

@app.route('/userhome')
def show_entries():
	query = 'select timestamp, liquid, qty from entries where username="'+session['username']+'"'
	cur = g.db.execute(query)
	entries = [dict(timestamp=row[0], liquid=row[1], qty=row[2]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)
		
def validate_user(username, password):
	error = None
	cur = g.db.execute('select username, password from accounts')
	for row in cur.fetchall():
		if username == row[0]:
			if password == row[1]:
				error = 'Login success'
				break
			else:
				error = 'Invalid password'
				break
	if error == None:
		error = 'Invalid username'
	return error
		
@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	timestamp = strftime("%b %d, %Y %H:%M:%S", localtime())
	liquid = request.form['liquid']
	qty = request.form['qty']
	username = session['username']
	#add_query = 'insert into entries (timestamp, liquid, qty, username) values (?, ?, ?, ?)', [timestamp, liquid, qty, username]
	#print add_query
	g.db.execute('insert into entries (timestamp, liquid, qty, username) values (?, ?, ?, ?)', [timestamp, liquid, qty, username])
	g.db.commit()
	flash('New entry was successfully added')
	return redirect(url_for('show_entries'))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		form_username = request.form['username'] 
		form_password = request.form['password'] 
		error = validate_user(form_username, form_password)
		if error == 'Login success':
			session['logged_in'] = True
			session['username'] = form_username
			flash('Welcome ' + form_username)
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['username'] == '':
			error = 'Blank username'
		elif request.form['password'] == '':
			error = 'Blank password'
		else:
			g.db.execute('insert into accounts (username, password) values (?, ?)', [request.form['username'], request.form['password']])
			g.db.commit()
			flash('You are registered!')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)
	
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You are logged out')
	return redirect(url_for('home'))
		
if __name__ == '__main__':
	app.run()
	
