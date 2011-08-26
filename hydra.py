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


# Database stuff
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


# Utility Functions

def count_userbase():
	"""
	Calculate the number of registered users
	"""
	count = g.db.execute('select COUNT(username) from accounts')
	usercount = count.fetchall()
	return usercount[0]

	
def calculate_stats(entries):
	"""
	Calculate the amount of liquids every consumed.
	Calculate the count of each category of liquids consumed
	"""
	total_qty = 0
	liquid_dict = {}
	for entry in entries:
		# dictionary initializations
		liquid_dict[entry['liquid']] = 0
	for entry in entries:
		# var reassign
		timestamp = entry['timestamp']
		liquid = entry['liquid']
		qty = entry['qty']
		# categorized consumption
		liquid_dict[liquid] += 1
		# total liquid consumption
		total_qty += int(qty)
	# convert into dict for ease of page rendering
	liquid_ctgry_cnt = [dict(category=liq, count=cnt) for liq, cnt in liquid_dict.iteritems()]
	return total_qty, liquid_ctgry_cnt
	
			
def calculate_graph(entries):
	"""
	Calculate the amount of liquids consumed per day
	"""
	day_consumption = {}
	for entry in entries:
		# dictionary initializations
		timestamp = entry['timestamp']
		day_consumption[timestamp[:12]] = 0
	for entry in entries:
		# var reassign
		timestamp = entry['timestamp']
		qty = entry['qty']
		# daily consumption
		day_consumption[timestamp[:12]] += int(qty)
	# convert into dict for ease of page rendering
	daily_consumption = [dict(date=date, qty=qty) for date, qty in day_consumption.iteritems()]
	return daily_consumption
		
		
def calculate_time_delta(entries):
	"""
	"""
	day_consumption = {}
	for entry in entries:
		# dictionary initializations
		last_tm = entry['timenum']
		break
	from datetime import datetime
	# last consumed timestamp
	year = int(last_tm[:4])
	month = int(last_tm[4:7])
	day = int(last_tm[7:10])
	hour = int(last_tm[10:13])
	mins = int(last_tm[13:16])
	start = datetime(year, month, day, hour, mins)
	# current time
	dt = localtime()
	c_year = dt.tm_year
	c_month = dt.tm_mon
	c_day = dt.tm_mday
	c_hour = dt.tm_hour
	c_mins = dt.tm_min
	end = datetime(c_year, c_month, c_day, c_hour, c_mins)
	delta = end-start
	return str(delta)
	

def validate_user(username, password):
	"""
	Validate the user trying to login
	"""
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


# URLS
		
@app.route('/')
def home():
	for usercount in count_userbase(): pass
	username = session['username'].capitalize()
	return render_template('home.html', user=username, usercount=usercount)


@app.route('/userhome')
def show_entries():
	parched_time = 0
	query = 'select timestamp, liquid, qty, timestamp_num from entries where username="'+session['username']+'" order by id desc'
	cur = g.db.execute(query)
	entries = [dict(timestamp=row[0], liquid=row[1], qty=row[2], timenum=row[3]) for row in cur.fetchall()]
	username = session['username'].capitalize()
	count = g.db.execute('select COUNT(*) from entries where username="'+session['username']+'"')
	ecount = count.fetchall()
	for entry_count in ecount[0]: pass
	if entry_count > 0: parched_time = calculate_time_delta(entries)
	# calculate statistics
	total_qty, liquid_ctgry_cnt = calculate_stats(entries)
	# calculate graph
	daily_consumption = calculate_graph(entries)
	# render
	return render_template('show_entries.html', entries=entries, user=username, \
		entry_count=entry_count, total_qty=total_qty, liquid_ctgry_cnt=liquid_ctgry_cnt, \
		daily_consumption=daily_consumption, parched_time=parched_time)
	
		
@app.route('/alerts')
def alerts():
	parched_time = calculate_time_delta(entries)
	

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	timestamp = strftime("%b %d, %Y %H:%M:%S", localtime())
	timestamp_num = strftime("%Y %m %d %H %M", localtime()) # for calculating time deltas easier
	liquid = request.form['liquid']
	qty = request.form['qty']
	username = session['username']
	g.db.execute('insert into entries (timestamp, timestamp_num, liquid, qty, username) values (?, ?, ?, ?, ?)', \
		[timestamp, timestamp_num, liquid, qty, username])
	g.db.commit()
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


# Main
		
if __name__ == '__main__':
	app.run()
	
