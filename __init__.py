# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 09:41:31 2018

@author: qihen
"""

from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import pymysql.cursors
from passlib.hash import md5_crypt, pbkdf2_sha256
from datetime import datetime
import json

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
	return render_template('index.html')

@app.route('/search_flight', methods=['POST'])
def search_flight():
	rule = request.path
	print("*"*10, rule)
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	print(departure_airport)
	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND status LIKE "incoming" AND departure_time > now()'
	cursor.execute(query, (departure_airport, arrival_airport))
	data = cursor.fetchall()
	cursor.close()
	#print(data)
	return render_template('index.html', data = data)

@app.route('/logout')
def logout():
	session.pop('username', None)
	return render_template('index.html')

@app.route('/customer/login')
def login_customer():
	return render_template('login_customer.html')

# Authenticates the customer login
@app.route('/loginCustomerAuth', methods=['POST'])
def login_as_customer_auth():
	username = request.form['username']
	password = request.form['password']
	print(username)

	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s AND password = MD5(%s)'
	
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()

	error = None
	if data:
		# if pbkdf2_sha256.verify(password, data['password']):
		session['username'] = username
		return redirect(url_for('home_customer'))
		# else:
		# 	error = 'Invalid password'
		# 	return render_template('login_customer.html', error = error)
	else:
		error = 'Invalid username or wrong password'
		return render_template('login_customer.html', error = error)

@app.route('/agent/login')
def login_agent():
	#clear the session when log in
	session.clear()
	return render_template('login_agent.html')

# Authenticates the agent login
@app.route('/loginAgentAuth', methods=['POST'])
def login_as_agent_auth():
	username = request.form['username']
	password = request.form['password']
	print(username, password)
	
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s AND password = MD5(%s)'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if data:
		# if md5_crypt.verify(password, data['password']):
		session['username'] = username
		return redirect(url_for('home_agent'))
		# else:
		# 	error = 'Invalid password'
		# 	return render_template('login_agent.html', error = error)
	else:
		error = 'Invalid username or wrong password'
		return render_template('login_agent.html', error = error)

@app.route("/agent")
def home_agent():
	username = session['username']
	return render_template('home_agent.html', username=username)

@app.route('/staff/login')
def login_staff():
	#clear the session each time we log in
	session.clear()
	return render_template('login_staff.html')

# Authenticates the agent login
@app.route('/loginStaffAuth', methods=['POST'])
def login_as_staff_auth():
	username = request.form['username']
	password = request.form['password']
	
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s AND password = MD5(%s)'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if data:
		# if md5_crypt.verify(password, data['password']):
		session['username'] = username
		session['airline_name'] = data['airline_name'] if 'airline_name' in data else None
		return redirect(url_for('home_staff'))
		# else:
		# 	error = 'Invalid password'
		# 	return render_template('login_staff.html', error = error)
	else:
		error = 'Invalid username or wrong password'
		return render_template('login_staff.html', error = error)

#Define route for register
@app.route('/customer/register')
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
    
	if phone_number.isdigit() == False:
		error = 'Phone number needs to be number'
		return render_template('register_customer.html', error = error)

	# print("***************" + email + "*************** ")
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		cursor.close()
		error = "This email has already registered"
		return render_template('register_customer.html', error = error)
	else:
		# encoded_password = md5_crypt.hash(password)
		ins = 'INSERT INTO customer VALUES(%s,%s,MD5(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth ))
		conn.commit()
		cursor.close()
		return render_template('index.html', message='You have registered as a customer!')

@app.route("/customer")
def home_customer():
	username = session['username']
	return render_template('home_customer.html', username=username)

@app.route("/customer/view_flights")
def customer_view_flight():
	username = session['username']
	now = datetime.now()
	print(username)
	if authenticate(username, 'customer') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	query = 'SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND status LIKE "incoming" AND departure_time > now()'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.close()
	error = None
	return render_template("customer_view_flights.html", username=username, data=data)

@app.route("/customer/track_spending", methods=['GET', 'POST'])
def track_spending():
	username = session['username']
	if authenticate(username, 'customer') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	query = 'SELECT SUM(price) as expense FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND purchase_date > DATE_SUB(now(), INTERVAL 1 YEAR)'
	cursor.execute(query, (username))
	total = cursor.fetchone()
	error = None
	# get data for chart
	if request.form:
		start_date = request.form['start_date']
		end_date = request.form['end_date']
		start_d_conv = datetime.strptime(start_date, "%Y-%m-%d")
		end_d_conv = datetime.strptime(end_date, "%Y-%m-%d")
		month_diff = diff_month(end_d_conv, start_d_conv)
		print(start_date, end_date)
		print(month_diff)
		query = "SELECT YEAR(purchase_date) as year, MONTH(purchase_date) as month, sum(price) as expense FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND purchase_date BETWEEN %s AND %s GROUP BY YEAR(purchase_date), MONTH(purchase_date) DESC"
		cursor.execute(query, (username, start_date, end_date))
		data = cursor.fetchall()
		month = end_d_conv.month
		year = end_d_conv.year
		labels, values = get_labels(month, year, data, month_diff)
	else:
		query = "SELECT YEAR(purchase_date) as year, MONTH(purchase_date) as month, sum(price) as expense FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND purchase_date > DATE_SUB(now(), INTERVAL 6 MONTH) GROUP BY YEAR(purchase_date), MONTH(purchase_date) DESC"
		cursor.execute(query, (username))
		data = cursor.fetchall()
		now = datetime.now()
		month = now.month
		year = now.year
		labels, values = get_labels(month, year, data)
	cursor.close()
	return render_template("customer_track_spending.html", **locals())

@app.route('/customer/purchase')
def customer_purchase():
	username = session['username']
	if authenticate(username, 'customer') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	return render_template('customer_search_flights.html')

@app.route('/customer/purchase/book', methods=['POST'])
def customer_book_flight():
	# get ticket id
	username = session['username']
	if authenticate(username, 'customer') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	query = 'SELECT COUNT(*) FROM ticket'
	cursor.execute(query)
	ticket_num = cursor.fetchone()['COUNT(*)']
	print('*' * 10, ticket_num)
	# print(ticket_num)
	ticket_id = ticket_num + 1

	username = session['username']
	flight_num = request.form['flight_num']
	airline = request.form['airline']
	
	query = 'INSERT INTO ticket VALUE(%s, %s, %s)'
	cursor.execute(query, (str(ticket_id), airline, int(flight_num)))
	conn.commit()

	now = datetime.now()
	query = 'INSERT INTO purchases VALUE (%s, %s, NULL, %s)'
	cursor.execute(query, (str(ticket_id), username, str(now)))
	conn.commit()
	cursor.close()
	ticket_id += 1
	print(ticket_id)
	return render_template('customer_after_booking.html')

@app.route('/customer/purchase/search', methods=['POST'])
def customer_search_flight():
	username = session['username']
	if authenticate(username, 'customer') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	departure_time = request.form['departure_date']
	arrival_time = request.form['arrival_date']
	print(request.form)

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND status LIKE "incoming" AND DATE(departure_time) LIKE %s AND DATE(arrival_time) LIKE %s'
	cursor.execute(query, (departure_airport, arrival_airport, departure_time, arrival_time))
	data = cursor.fetchall()
	cursor.close()
	#print(data)
	return render_template('customer_search_flights.html', data = data)

#Define route for agent register
@app.route('/agent/register')
def registerasagent():
	 return render_template('register_agent.html')

#Authenticates the agent register
@app.route('/registerAgentAuth', methods=['GET', 'POST'])
def registerasagentAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	
	booking_agent_id = request.form['booking_agent_id']
	if booking_agent_id.isdigit() == False:
		error = 'ID needs to be numbers'
		return render_template('register_agent.html',error=error)

	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):         
		cursor.close()
		#If the previous query returns data, then user exists
		error = "This email has already registered"
		return render_template('register_agent.html', error = error)
	else:
		# encoded_password = md5_crypt.hash(password)
		ins = 'INSERT INTO booking_agent VALUES(%s,MD5(%s),%s)'
		cursor.execute(ins, (email, password, booking_agent_id ))
		conn.commit()
		cursor.close()
		print("register success")
		return render_template('index.html', message='You have registered as a booking agent!')

@app.route("/agent/view_flights")
def agent_view_flight():
	username = session['username']
	print(username)
	if authenticate(username, 'agent') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	# get booking agent id
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email LIKE %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	id = data['booking_agent_id']
	print("*"*10, id)
	
	query = 'SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent WHERE booking_agent_id = %s AND status LIKE "incoming"'
	cursor.execute(query, (id))
	data = cursor.fetchall()
	print(data)
	error = None
	return render_template("agent_view_flights.html", username=username, data=data)

@app.route('/agent/purchase')
def agent_purchase():
	username = session['username']
	if authenticate(username, 'agent') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	return render_template('agent_search_flights.html')

@app.route('/agent/purchase/search', methods=['POST'])
def agent_search_flight():
	username = session['username']
	if authenticate(username, 'agent') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	departure_time = request.form['departure_date']
	arrival_time = request.form['arrival_date']
	print(request.form)

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND status LIKE "incoming" AND DATE(departure_time) LIKE %s AND DATE(arrival_time) LIKE %s'
	cursor.execute(query, (departure_airport, arrival_airport, departure_time, arrival_time))
	data = cursor.fetchall()
	#print(data)
	return render_template('agent_search_flights.html', data = data)

@app.route('/agent/purchase/book', methods=['POST'])
def agent_book_flight():
	# get ticket id
	username = session['username']
	if authenticate(username, 'agent') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	query = 'SELECT COUNT(*) FROM ticket'
	cursor.execute(query)
	ticket_num = cursor.fetchone()['COUNT(*)']
	print('*' * 10, ticket_num)
	# print(ticket_num)
	ticket_id = ticket_num + 1

	# get agent id
	username = session["username"]
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email LIKE %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	id = data['booking_agent_id']
	flight_num = request.form['flight_num']
	airline = request.form['airline']
	customer_email = request.form['customer_email']
	
	query = 'INSERT INTO ticket VALUE(%s, %s, %s)'
	cursor.execute(query, (str(ticket_id), airline, int(flight_num)))
	conn.commit()

	now = datetime.now()
	query = 'INSERT INTO purchases VALUE (%s, %s, %s, %s)'
	cursor.execute(query, (str(ticket_id), customer_email, id, str(now)))
	conn.commit()
	cursor.close()
	ticket_id += 1
	return render_template('agent_after_booking.html')

@app.route('/agent/view_commission', methods=["GET", "POST"])
def agent_view_commission():
	cursor = conn.cursor()
	username = session["username"]
	if authenticate(username, 'agent') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email LIKE %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	id = data['booking_agent_id']
	print(id)
	query = 'SELECT count(*) AS num_tickets, 0.1 * SUM(price) AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent WHERE booking_agent_id = %s AND status LIKE "incoming" AND purchase_date > DATE_SUB(now(), INTERVAL 1 MONTH)'
	cursor.execute(query, id)
	data = cursor.fetchone()
	data_range = 0

	if request.form:
		start_date = request.form['start_date']
		end_date = request.form['end_date']
		query = 'SELECT count(*) AS num_tickets, 0.1 * SUM(price) AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent WHERE booking_agent_id = %s AND status LIKE "incoming" AND purchase_date BETWEEN %s and %s'
		cursor.execute(query, (id, start_date, end_date))
		data_range = cursor.fetchone()
		print(data_range)

	return render_template('agent_view_commission.html', **locals())

@app.route("/agent/top_customers", methods=['POST', 'GET'])
def agent_top_customers():
	cursor = conn.cursor()
	username = session["username"]
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email LIKE %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	id = data['booking_agent_id']
	print(id)

	query = 'SELECT customer_email, COUNT(*) AS num FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent WHERE booking_agent_id = %s AND purchase_date > DATE_SUB(now(), INTERVAL 1 MONTH) GROUP BY customer_email ORDER BY num DESC LIMIT 5'
	cursor.execute(query, id)
	data = cursor.fetchall()
	print("*" * 10)
	print(data)
	legend1 = 'top customers (number of tickets)'
	labels1 = []
	values1 = []
	for d in data:
		labels1.append(d['customer_email'])
		values1.append(int(d['num']))
	print(labels1)

	query = 'SELECT customer_email, SUM(price) * 0.1 AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent WHERE booking_agent_id = %s AND purchase_date > DATE_SUB(now(), INTERVAL 1 MONTH) GROUP BY customer_email ORDER BY commission DESC LIMIT 5'
	cursor.execute(query, id)
	data = cursor.fetchall()
	print("*" * 10)
	print(data)
	labels2 = []
	values2 = []
	legend2 = 'top customers (total commission)'
	for d in data:
		labels2.append(d['customer_email'])
		values2.append(int(d['commission']))
	print(values2)
	
	return render_template('agent_view_top_customers.html', **locals())



#Define route for agent staff
@app.route('/staff/register')
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
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):      
		cursor.close()	
		#If the previous query returns data, then user exists
		error = "This username has already registered"
		return render_template('register_staff.html', error = error)
	else:
		# encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO airline_staff VALUES(%s,MD5(%s),%s, %s,%s,%s)'
		cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
		conn.commit()
		cursor.close()
		return render_template('index.html', message='You have registered as an airline staff !')

@app.route("/staff",methods = ['GET','POST'])
def home_staff():
	#if the button has been triggered
	if request.method == 'POST':
		if "start_date" in request.form:
			start_date = request.form['start_date']
			end_date = request.form['end_date'] if 'end_date' in request.form else 'NOW()'
			departure_airport = request.form['departure_airport'] 
			arrival_airport = request.form['arrival_airport'] 
			#departure_city = '= ' + request.form['departure_city'] if 'departure_city' in request.form else 'IS NOT NULL'
			#arrival_city = '= ' + request.form['arrival_city'] if 'arrival_city' in request.form else 'IS NOT NULL'
			cursor = conn.cursor()
			query = ('SELECT * FROM flight JOIN airport T JOIN airport S where departure_airport = T.airport_name AND arrival_airport = S.airport_name '
					'AND departure_time >= %s AND arrival_time <= %s AND departure_airport = %s AND arrival_airport = %s')
			cursor.execute(query, (start_date, end_date, departure_airport, arrival_airport))
			data = cursor.fetchall()
			cursor.close()
			return render_template('home_staff.html', username=session['username'], result=data, airline_name=session['airline_name'])
			
		#if we try to update the status
		elif 'update_status' in request.form:
			airline_name = request.form['airline_name']
			flight_num = request.form['flight_num']
			cursor = conn.cursor()
			new_status = request.form['update_status']
			query = "UPDATE flight SET status = %s WHERE airline_name = %s and flight_num = %s"
			cursor.execute(query, (new_status, airline_name, flight_num))
			conn.commit()
			msg = "Flight %s state has been successfully updated to %s" % (flight_num, new_status)
			query = 'SELECT * FROM flight WHERE departure_time >= NOW() and departure_time < NOW() + INTERVAL 30 DAY and airline_name = %s'
			cursor.execute(query, airline_name)
			data = cursor.fetchall()
			cursor.close()
			return render_template('home_staff.html', username=session['username'], result=data, airline_name=airline_name, message=msg)
		#if instead we would like to view the passengers
		else:		
			airline_name = request.form['airline_name']
			flight_num = request.form['flight_num']
			cursor = conn.cursor()
			query = 'SELECT DISTINCT name, email FROM purchases, ticket, customer WHERE ticket.ticket_id = purchases.ticket_id and customer_email = email and airline_name = %s and flight_num = %s'
			cursor.execute(query, (airline_name, flight_num))
			passengers = cursor.fetchall()
			cursor.close()
			return render_template('home_staff.html', airline_name=airline_name, flight_num=flight_num, passengers=passengers)
	else:
		username = session['username']
		airline_name = session['airline_name']
		query = 'SELECT * FROM flight WHERE departure_time >= NOW() and departure_time < NOW() + INTERVAL 30 DAY and airline_name = %s'
		cursor = conn.cursor()
		cursor.execute(query, airline_name)
		data = cursor.fetchall()
		cursor.close()
		return render_template('home_staff.html', username=username, result=data, airline_name=airline_name)

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	if request.method == 'POST':
		airline_name = request.form['airline_name']
		flight_num = request.form['flight_num']
		departure_airport = request.form['departure_airport']
		departure_time = request.form['departure_time']
		arrival_airport = request.form['arrival_airport']
		arrival_time = request.form['arrival_time']
		price = request.form['price']
		status = request.form['status']
		airplane_id = request.form['airplane_id']
		cursor = conn.cursor()
		query = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(query,(airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id))
		conn.commit()
		msg = "You have successfully added Flight %s" % flight_num
		query = 'SELECT * FROM flight WHERE departure_time >= NOW() and departure_time < NOW() + INTERVAL 30 DAY and airline_name = %s'
		cursor.execute(query, (airline_name))
		data = cursor.fetchall()
		cursor.close()
		return render_template('home_staff.html', username=session['username'], result=data, airline_name=airline_name, message=msg)
	else:
		return render_template('create_flight.html', airline_name=session['airline_name'])

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	if request.method == 'GET':
		cursor = conn.cursor()
		query = 'SELECT * FROM airplane WHERE airline_name = %s'
		cursor.execute(query,(session['airline_name']))
		data = cursor.fetchall()
		cursor.close()
		return render_template('add_airplane.html', username=session['username'], result=data, airline_name=session['airline_name'])
	else:
		airline_name = request.form['airline_name']
		airplane_id = request.form['airplane_id']
		seats = request.form['seats']
		query = 'INSERT INTO airplane VALUES(%s, %s, %s)'
		cursor = conn.cursor()
		cursor.execute(query, (airline_name, airplane_id, seats))
		conn.commit()
		msg = 'Airplane %s has been successfully added' % airplane_id
		query = 'SELECT * FROM airplane WHERE airline_name = %s'
		cursor.execute(query,(session['airline_name']))
		data = cursor.fetchall()
		cursor.close()
		return render_template('add_airplane.html', username=session['username'], result=data, airline_name=session['airline_name'], message=msg)

@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	if request.method == 'POST':
		airline_name = request.form['airline_name']
		airport_name = request.form['airport_name']
		airport_city = request.form['airport_city']
		query = 'INSERT INTO airport VALUES(%s, %s)'
		cursor = conn.cursor()
		cursor.execute(query, (airport_name, airport_city))
		conn.commit()
		msg = 'Airport %s in %s has been successfully added' % (airport_name, airport_city)
		query = 'SELECT * FROM flight WHERE departure_time >= NOW() and departure_time < NOW() + INTERVAL 30 DAY and airline_name = %s'
		cursor = conn.cursor()
		cursor.execute(query, airline_name)
		data = cursor.fetchall()
		cursor.close()
		return render_template('home_staff.html', username=session['username'], result=data, airline_name=airline_name, message = msg)
	else:
		return render_template('add_airport.html', airline_name=session['airline_name'])

@app.route('/view_booking_agents', methods=['GET', 'POST'])
def view_booking_agents():
	#Top 5 booking agents based on number of tickets sales for the past month and past year. 
	#Top 5 booking agents based on the amount of commission received for the last year.
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	cursor = conn.cursor()
	query1month = ('SELECT booking_agent_id, COUNT(*) as ticket_sold FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket WHERE '
					'airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 MONTH '
					'GROUP BY booking_agent_id ORDER BY ticket_sold DESC LIMIT 5')
	cursor.execute(query1month, session['airline_name'])
	data1month = cursor.fetchall()
	
	query1year = ('SELECT booking_agent_id, COUNT(*) as ticket_sold FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket WHERE '
					'airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 YEAR '
					'GROUP BY booking_agent_id ORDER BY ticket_sold DESC LIMIT 5')
	cursor.execute(query1year, session['airline_name'])
	data1year = cursor.fetchall()
	
	query1year_com = ('SELECT booking_agent_id, SUM(price) as total_commission FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight '
						'WHERE airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 YEAR '
						'GROUP BY booking_agent_id ORDER BY total_commission LIMIT 5')
	cursor.execute(query1year_com, session['airline_name'])
	data1year_com = cursor.fetchall()
	
	cursor.close()	
	return render_template('view_booking_agents.html', airline_name=session['airline_name'], result1month=data1month, result1year=data1year, result1year_com=data1year_com)
	
@app.route('/view_frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	if request.method == 'POST':
		email = request.form['customer_email']
		return redirect(url_for('show_trips', airline_name=session['airline_name'], customer_email=email))
	else:
		query = ('SELECT customer_email, name, COUNT(*) AS travels FROM purchases natural JOIN ticket, customer '
				'WHERE customer_email = email AND airline_name = %s and purchase_date > NOW() - INTERVAL 1 YEAR '
				'GROUP BY customer_email ORDER BY travels DESC')
		cursor = conn.cursor()
		cursor.execute(query, session['airline_name'])
		data = cursor.fetchall()
		cursor.close()
		return render_template('view_frequent_customers.html', airline_name=session['airline_name'], result=data)

@app.route('/show_trips')
def show_trips():
	customer_email = request.args.get('customer_email')
	airline_name = session['airline_name']
	query = 'SELECT ticket_id, purchase_date, flight_num FROM purchases NATURAL JOIN ticket, customer WHERE customer_email = email AND airline_name = %s AND customer_email = %s'
	cursor = conn.cursor()
	cursor.execute(query, (airline_name, customer_email))
	data = cursor.fetchall()
	cursor.close()
	return render_template('show_trips.html', airline_name=airline_name, result=data, customer_email=customer_email)

#todo: visualize the report
@app.route('/report', methods=['GET', 'POST'])
def report():
	if request.method == 'POST':
		airline_name = session['airline_name']
		if 'start_date' in request.form:
			start_date = request.form['start_date']
			end_date = request.form['end_date'] if 'end_date' in request.form else 'NOW()'
			cursor = conn.cursor()
			query = 'SELECT * FROM ticket NATURAL JOIN purchases WHERE airline_name = %s AND purchase_date >= %s AND purchase_date <= %s'
			cursor.execute(query, (airline_name, start_date, end_date))
			Num_ticket = len(cursor.fetchall())
			cursor.close()
			msg = "From %s to %s the number of sold tickets is: " %(start_date, end_date)
			return render_template('report.html', airline_name = airline_name, result = Num_ticket, message = msg)
		elif request.form['interval'] == 'MONTH':
			cursor = conn.cursor()
			query = 'SELECT * FROM ticket NATURAL JOIN purchases WHERE airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 MONTH'
			cursor.execute(query, (airline_name))
			Num_ticket = len(cursor.fetchall())
			cursor.close()
			msg = 'the number of sold tickets in the last month is: '
			return render_template('report.html', airline_name= airline_name, result=Num_ticket, message=msg)
		elif request.form['interval'] == 'YEAR':
			cursor = conn.cursor()
			count = []
			for i in range(12, 0, -1):
				query = 'SELECT * FROM ticket NATURAL JOIN purchases WHERE airline_name = %s AND purchase_date < NOW() - INTERVAL %s MONTH and purchase_date >= NOW() - INTERVAL %s MONTH'
				cursor.execute(query, (session['airline_name'], i-1, i))
				count.append(len(cursor.fetchall()))
			cursor.close()
			totSellNum = sum(count)
			msg = 'Number of tickets sold for the last year: '
			return render_template('report.html', airline_name=session['airline_name'], sellStats=count, totSellNum=totSellNum, message=msg)
	else:
		airline_name = session['airline_name']
		return render_template('report.html', airline_name= airline_name)

@app.route('/show_revenue_last_month')
def last_month_revenue():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	airline_name = session['airline_name']
	cursor = conn.cursor()
	query_direct = 'SELECT SUM(price) AS direct_revenue FROM ticket NATURAL JOIN flight NATURAL JOIN purchases where airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 MONTH AND booking_agent_id IS NULL'
	cursor.execute(query_direct, airline_name)
	data_direct = cursor.fetchone()
	
	query_indirect = 'SELECT SUM(price) AS indirect_revenue FROM ticket NATURAL JOIN flight NATURAL JOIN purchases where airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 MONTH AND booking_agent_id IS NOT NULL'
	cursor.execute(query_indirect, airline_name)
	data_indirect = cursor.fetchone()
	cursor.close()
	
	data = []
	data.append(float(data_direct['direct_revenue']) if data_direct['direct_revenue'] else 0)
	data.append(float(data_indirect['indirect_revenue']) if data_indirect['indirect_revenue'] else 0)

	return render_template('last_month_revenue.html', airline_name = airline_name, result = data)

@app.route('/show_revenue_last_year')
def last_year_revenue():
	username = session["username"]
	if authenticate(username, 'staff') == 'failed':
		session.pop('username', None)
		return render_template('index.html')
	airline_name = session['airline_name']
	cursor = conn.cursor()
	query_direct = 'SELECT SUM(price) AS direct_revenue FROM ticket NATURAL JOIN flight NATURAL JOIN purchases where airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 YEAR AND booking_agent_id IS NULL'
	cursor.execute(query_direct, airline_name)
	data_direct = cursor.fetchone()
	
	query_indirect = 'SELECT SUM(price) AS indirect_revenue FROM ticket NATURAL JOIN flight NATURAL JOIN purchases where airline_name = %s AND purchase_date <= NOW() and purchase_date > NOW() - INTERVAL 1 YEAR AND booking_agent_id IS NOT NULL'
	cursor.execute(query_indirect, airline_name)
	data_indirect = cursor.fetchone()
	cursor.close()
	
	data = []
	data.append(float(data_direct['direct_revenue']) if data_direct['direct_revenue'] else 0)
	data.append(float(data_indirect['indirect_revenue']) if data_indirect['indirect_revenue'] else 0)

	return render_template('last_year_revenue.html', airline_name = airline_name, result = data)

@app.route('/top_destinations')
def top_destinations():
	#Find the top 3 most popular destinations for last 3 months and last year
	cursor = conn.cursor()
	query3month =  ('SELECT airport_city, COUNT(*) AS ticket_sold '
					'FROM (SELECT airport_city, arrival_airport '
						'FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport '
						'WHERE airline_name = %s AND departure_time >= NOW() - INTERVAL 3 MONTH AND arrival_airport = airport_name) as T '
					'GROUP BY airport_city ORDER BY ticket_sold DESC LIMIT 3')
	cursor.execute(query3month, session['airline_name'])
	data3month = cursor.fetchall()
	query1year =   ('SELECT airport_city, COUNT(*) AS ticket_sold '
					'FROM (SELECT airport_city, arrival_airport '
						'FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport '
						'WHERE airline_name = %s AND departure_time >= NOW() - INTERVAL 1 YEAR AND arrival_airport = airport_name) as T '
					'GROUP BY airport_city ORDER BY ticket_sold DESC LIMIT 3')
	cursor.execute(query1year, session['airline_name'])
	data1year = cursor.fetchall()
	cursor.close()
	return render_template('top_destinations.html', airline_name=session['airline_name'], result3month=data3month, result1year=data1year)

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
			cursor.close()
			return render_template('guest_home.html', result=data)
		else:
			return render_template('guest_home.html', error="Please enter departure city/airport, arrival city/airport and travel date")
	else:
		return render_template('guest_home.html')

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month + 1

def get_labels(month, year, data, diff=6):
	labels = []
	values = []
	item_found = 0
	print(diff)
	for i in range(diff):
		labels.append("%s-%s" % (str(year), str(month)))
		for j in range(len(data)):
			if data[j]['year'] == year and data[j]['month'] == month:
				values.append(int(data[j]['expense']))
				item_found = 1
				break
		if item_found == 0:
			values.append(0)
		month -= 1
		if month == -1:
			month = 12
			year -= 1
		item_found = 0

	labels.reverse()
	values.reverse()
	print(labels)
	print(values)
	return labels, values

def authenticate(username, usertype):
	print(username, usertype)
	print(type(username), type(usertype))
	cursor = conn.cursor()
	if usertype == 'customer':
		query = 'SELECT * FROM customer WHERE email LIKE %s'
	elif usertype == 'agent':
		query = 'SELECT * FROM booking_agent WHERE email LIKE %s'
	elif usertype == 'staff':
		query = 'SELECT * FROM airline_staff WHERE username LIKE %s'
	cursor.execute(query, username)
	data = cursor.fetchone()
	cursor.close()
	if data:
		return "success"
	else:
		return "failed"
	
	

if __name__ == '__main__':
	app.run('127.0.0.1', 5000, debug = True)


