# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 09:41:31 2018

@author: qihen
"""

from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from passlib.hash import md5_crypt

#initialize the app
app = Flask(__name__)

#configure db
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline',
                       charset='utf8mb4',
                       port=3307,
                       cursorclass=pymysql.cursors.DictCursor)

#give the secret key
app.secret_key = 'some key'

#Define a route to hello function
@app.route('/')
def hello():
	cur = conn.cursor()
	cur.execute("SELECT * FROM flight")
	data = cur.fetchall()
	print(data)
	return render_template('index.html', data = data)

@app.route('/login_customer')
def login_customer():
	return render_template('login_customer.html')

# Authenticates the customer login
@app.route('/loginCustomerAuth', methods=['POST'])
def login_as_customer_auth():
	username = request.form['username']
	password = request.form['password']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	error = None
	if data:
		if md5_crypt.verify(password, exist['password']):
			return redirect(url_for('customer_home'))
		else:
			error = 'Invalid password'
			return render_template('login_customer.html', error = error)
	else:
		error = 'Invalid username'
		return render_template('login_customer.html', error = error)
	
@app.route('/login_agent')
def login_agent():
	return render_template('login_agent.html')

# Authenticates the agent login
@app.route('/loginAgentAuth', methods=['POST'])
def login_as_agent_auth():
	username = request.form['username']
	password = request.form['password']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s AND password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	error = None
	if data:
		if md5_crypt.verify(password, exist['password']):
			return redirect(url_for('agent_home'))
		else:
			error = 'Invalid password'
			return render_template('login_agent.html', error = error)
	else:
		error = 'Invalid username'
		return render_template('login_agent.html', error = error)

@app.route('/login_staff')
def login_staff():
	return render_template('login_staff.html')

# Authenticates the agent login
@app.route('/loginStaffAuth', methods=['POST'])
def login_as_staff_auth():
	username = request.form['username']
	password = request.form['password']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE email = %s AND password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	error = None
	if data:
		if md5_crypt.verify(password, exist['password']):
			return redirect(url_for('agent_home'))
		else:
			error = 'Invalid password'
			return render_template('login_staff.html', error = error)
	else:
		error = 'Invalid username'
		return render_template('login_staff.html', error = error)


#Define route for register
@app.route('/register_customer')
def register_customer():
	return render_template('register_customer.html')

#Authenticates the customer register
@app.route('/registerCustomerAuth', methods=['GET', 'POST'])
def registerascustomerAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	name = request.form['name']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = request.form['phone_number']
	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']
        
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		
		#If the previous query returns data, then user exists
		error = "This email has already registered"
		return render_template('register_customer.html', error = error)
	else:
		encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		cursor.execute(ins, (email, encoded_password, name, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth ))
		conn.commit()
		cursor.close()
		return render_template('index.html')

#Define route for agent register
@app.route('/register_agent')
def registerasagent():
	 return render_template('register_agent.html')
 
#Authenticates the agent register
@app.route('/registerAgentAuth', methods=['GET', 'POST'])
def registerasagentAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	booking_agent_id = request.form['booking_agent_id']

	cursor = conn.cursor()
	query = 'SELECT * FROM user WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):         
		#If the previous query returns data, then user exists
		error = "This email has already registered"
		return render_template('register_agent.html', error = error)
	else:
		encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO booking_agent VALUES(%s,%s,%s)'
		cursor.execute(ins, (email, encoded_password, booking_agent_id ))
		conn.commit()
		cursor.close()
		return render_template('index.html')

#Define route for agent staff
@app.route('/register_staff')
def registerasstaff():
	return render_template('register_staff.html')

@app.route('/registerStaffAuth', methods=['GET', 'POST'])
def registerasstaffAuth():
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline_name = request.form['airline_name']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):         
		#If the previous query returns data, then user exists
		error = "This username has already registered"
		return render_template('register_staff.html', error = error)
	else:
		encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO airline_staff VALUES(%s,%s,%s, %s,%s,%s)'
		cursor.execute(ins, (username, encoded_password, first_name, last_name, date_of_birth, airline_name))
		conn.commit()
		cursor.close()
		return render_template('index.html')

#for the guest, you can directly search the flight
@app.route('/guest_home', methods=['GET', 'POST'])
def guest_home():
	if request.method == 'POST':
		if request.form['departure_airport'] and request.form['arrival_airport'] and request.form['departure_date']:
			query = 'SELECT * FROM flight WHERE departure_time LIKE %s and departure_airport = %s and arrival_airport = %s'
			args = request.form['departure_date'] + '%', request.form['departure_airport'], request.form['arrival_airport']
			cursor = conn.cursor()
			cursor.execute(query, args)
			data = cursor.fetchall()
			return render_template('guest_home.html', result=data)
		else:
			return render_template('guest_home.html', error="Please enter departure city/airport, arrival city/airport and travel date")
	else:
		return render_template('guest_home.html')

if __name__ == '__main__':
	app.run('127.0.0.1', 5000, debug = True)
