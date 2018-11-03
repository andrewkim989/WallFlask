from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')

mysql = connectToMySQL('wall')

app = Flask(__name__)
app.secret_key = "Secretwall"

@app.route('/')
def index():
    return render_template("simpleindex.html")

@app.route('/rprocess', methods = ['POST'])
def register():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    password_con = request.form['password_con']
    
    if len(firstname) < 2:
        flash(u"The first name should be two or more characters long.", 'firstname')
    elif not name_regex.match(firstname):
        flash(u"The first name should not contain any numbers"
        " or any special characters.", 'firstname')
    
    if len(lastname) < 2:
        flash(u"The last name should be two or more characters long.", 'lastname')
    elif not name_regex.match(lastname):
        flash(u"The last name should not contain any numbers"
        " or any special characters.", 'lastname')
    
    query = "SELECT EXISTS (SELECT * FROM wall WHERE email = %(email)s) AS email"
    data = {
        'email': email
    }
    emailisthere = mysql.query_db(query, data)
        
    if len(email) < 1:
        flash(u"Email cannot be blank.", 'email')
    elif not EMAIL_REGEX.match(email):
        flash(u"Invalid Email Address.", 'email')
    elif emailisthere[0]['email'] != 0:
        flash("The email already exists in the system. Please type another one.")
    
    if len(password) < 1:
        flash(u"Please enter your password.", 'password')
    elif len(password) < 8:
        flash(u"Password should be more than 8 characters long.", 'password')
    elif re.search('[0-9]', password) is None:
        flash(u"Make sure that your password has a number in it", 'password')
    elif re.search('[A-Z]', password) is None: 
        flash(u"Make sure that your password has a capital letter in it", 'password')

    if len(password_con) < 1:
        flash(u"Please verify your password.", 'password_con')
    elif password != password_con:
        flash(u"Password does not match.", 'password_con')
    
    if '_flashes' in session.keys():
        return redirect("/")
    else:
        query = "INSERT INTO wall (firstname, email, password) VALUES (%(firstname)s, %(email)s, %(password)s);"
        data = {
            'firstname': firstname,
            'email': email,
            'password': password
        }
        mysql.query_db(query, data)
        session['email'] = email

        session['firstname'] = firstname
        return redirect('/home')

@app.route('/lprocess', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    query = "SELECT * FROM wall;"
    entries = mysql.query_db(query)

    emailexists = False

    for entry in entries:
        if entry['email'] == email:
            emailexists = True
            if entry['password'] == password:
                session['id'] = entry['id']
                session['firstname'] = entry['firstname']
                print (session['id'])
                return redirect('/home')
            else:
                flash(u"Incorrect password. Please try again.", 'password')
            break
    if emailexists is False:
        flash("The email does not exist in the system. Please type another one.", 'email')

    if '_flashes' in session.keys():
        return redirect("/")

@app.route('/home')
def home():
    query = f"SELECT * FROM wall WHERE id != {session['id']};"
    userlist = mysql.query_db(query)

    query2 = f"SELECT * FROM message WHERE receivername = '{session['firstname']}';"
    messagelist = mysql.query_db(query2)
    
    query3 = f"SELECT COUNT(*) as rec from message where receivername = '{session['firstname']}';"
    received = mysql.query_db(query3)

    query4 = f"SELECT COUNT(*) as sent from message where sendername = '{session['firstname']}';"
    sent = mysql.query_db(query4)

    return render_template('simplesuccess.html', users = userlist, messages = messagelist, r = received[0]['rec'], s = sent[0]['sent'])

@app.route('/send', methods = ['POST'])
def send():
    query = "INSERT INTO message (message, sendername, created_at, receivername) VALUES (%(message)s, %(sendername)s, NOW(), %(receivername)s);"
    data = {
        'message': request.form['message'],
        'sendername': session['firstname'],
        'receivername': request.form['receiver']
    }
    mysql.query_db(query, data)
    return redirect('/home')

if __name__=="__main__":
    app.run(debug = True) 