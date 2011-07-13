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
	
@app.route('/')
def show_entries():
	cur = g.db.execute('select liquid, qty from entries order by id desc')
	entries = [dict(liquid=row[0], qty=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)
	
@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries (liquid, qty) values (?, ?)', [request.form['liquid'], request.form['qty']])
	g.db.commit()
	flash('New entry was successfully added')
	return redirect(url_for('show_entries'))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
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
	return redirect(url_for('show_entries'))
		
if __name__ == '__main__':
	app.run()
	
