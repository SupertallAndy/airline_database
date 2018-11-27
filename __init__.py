# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 09:41:31 2018

@author: qihen
"""

from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import pymysql.cursors
from passlib.hash import md5_crypt
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
	query = 'SELECT * FROM flight WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND status LIKE "incoming"'
	cursor.execute(query, (departure_airport, arrival_airport))
	data = cursor.fetchall()
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
	query = 'SELECT * FROM customer WHERE email = %s'
	
	cursor.execute(query, (username))
	data = cursor.fetchone()

	error = None
	if data:
		if md5_crypt.verify(password, data['password']):
			session['username'] = username
			return redirect(url_for('home_customer'))
		else:
			error = 'Invalid password'
			return render_template('login_customer.html', error = error)
	else:
		error = 'Invalid username'
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
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if data:
		if md5_crypt.verify(password, data['password']):
			return redirect(url_for('home_agent'))
		else:
			error = 'Invalid password'
			return render_template('login_agent.html', error = error)
	else:
		error = 'Invalid username'
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
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if data:
		if md5_crypt.verify(password, data['password']):
			session['username'] = username
			session['airline_name'] = data['airline_name'] if 'airline_name' in data else None
			return redirect(url_for('home_staff'))
		else:
			error = 'Invalid password'
			return render_template('login_staff.html', error = error)
	else:
		error = 'Invalid username'
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
    
	print("***************" + email + "*************** ")
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
		error = "This email has already registered"
		return render_template('register_customer.html', error = error)
	else:
		encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		cursor.execute(ins, (email, name, encoded_password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth ))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route("/customer")
def home_customer():
	username = session['username']
	return render_template('home_customer.html', username=username)

@app.route("/customer/view_flights")
def customer_view_flight():
	username = session['username']
	print(username)
	cursor = conn.cursor()
	query = 'SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND status LIKE "incoming"'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	error = None
	return render_template("customer_view_flights.html", username=username, data=data)

@app.route("/customer/track_spending")
def track_spending():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND purchase_date > DATE_SUB(now(), INTERVAL 1 YEAR)'
	cursor.execute(query, (username))
	total = cursor.fetchone()
	print(total)
	error = None
	# get data for chart
	query = "SELECT YEAR(purchase_date) as year, MONTH(purchase_date) as month, sum(price) as expense FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email LIKE %s AND purchase_date > DATE_SUB(now(), INTERVAL 6 MONTH) GROUP BY YEAR(purchase_date), MONTH(purchase_date) DESC"
	cursor.execute(query, (username))
	data = cursor.fetchall()
	now = datetime.now()
	month = now.month
	year = now.year

	labels, values = get_labels(month, year, data)

	print("*" * 10, labels)
	print("*" * 10, values)
	return render_template("customer_track_spending.html", **locals())

@app.route("/customer/spending_barchart")
def spending_barchart():

	return render_template("customer_track_spending.html", **locals())

@app.route('/customer/purchase')
def customer_purchase():
	return render_template('customer_search_flights.html')

@app.route('/customer/purchase/book', methods=['POST'])
def customer_book_flight():
	# get ticket id
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
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	print(request.form)

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE departure_airport LIKE %s AND arrival_airport LIKE %s AND status LIKE "incoming"'
	cursor.execute(query, (departure_airport, arrival_airport))
	data = cursor.fetchall()
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

	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):         
		#If the previous query returns data, then user exists
		error = "This email has already registered"
		return render_template('register_agent.html', rerror = error)
	else:
		encoded_password = md5_crypt.encrypt(password)
		ins = 'INSERT INTO booking_agent VALUES(%s,%s,%s)'
		cursor.execute(ins, (email, encoded_password, booking_agent_id ))
		conn.commit()
		cursor.close()
		print("register success")
		return render_template('index.html')

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

@app.route("/staff",methods = ['GET','POST'])
def home_staff():
	#if the button has been triggered
	if request.method == 'POST':
		#if we try to update the status
		if 'update_status' in request.form:
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
			return render_template('staff_home.html', username=session['username'], result=data, airline_name=airline_name, message=msg)
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

#todo: view booking 

@app.route('/view_frequent_customers', methods=['GET', 'POST'])
def view_frequet_customers():
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
		return render_template('view_frequent_customers.html', airline_name=session['airline_name'], result=data)

@app.route('/show_trips')
def show_trips():
	customer_email = request.args.get('customer_email')
	airline_name = session['airline_name']
	query = 'SELECT ticket_id, purchase_date, flight_num FROM purchases NATURAL JOIN ticket, customer WHERE customer_email = email AND airline_name = %s AND customer_email = %s'
	cursor = conn.cursor()
	cursor.execute(query, (airline_name, customer_email))
	data = cursor.fetchall()
	return render_template('show_trips.html', airline_name=airline_name, result=data, customer_email=customer_email)

@app.route('/report', methods=['GET', 'POST'])
def report():
	return

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

def get_labels(month, year, data):
	labels = []
	values = []
	item_found = 0
	for i in range(6):
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
	return labels, values

if __name__ == '__main__':
	app.run('127.0.0.1', 5000, debug = True)


