from datetime import date
import random
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_login import session_protected
from flask_mysqldb import MySQL

app = Flask (__name__)
app.secret_key = "flash_message"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tonnytang01'
app.config['MYSQL_DB'] = 'karaoke'

mysql = MySQL(app)

users = {
    "user1@example.com": {
        "email": "user1@example.com",
        "password": "password1",
    },
    "user2@example.com": {
        "email": "user2@example.com",
        "password": "password2",
    },
    # Add more users if needed
}

admins = {
    "admin1@example.com": {
        "email": "admin1@example.com",
        "password": "password1",
    },
    # Add more users if needed
}

def save_user_mysql(first_name, last_name, birthday, email, area_code, phone, password):
    # Create a cursor to execute SQL queries
    cursor = mysql.connection.cursor()

    # Prepare the INSERT query with placeholders for the user data
    query = "INSERT INTO `user` (`first_name`, `last_name`, `birthday`,`email`, `area_code`, `phone`, `password`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (first_name, last_name, birthday, email, area_code, phone, password)

    # Execute the query and commit the changes to the database
    cursor.execute(query, values)
    mysql.connection.commit()

    # Close the cursor and database connection
    cursor.close()
    mysql.connection.close()

def check_user_credentials(email, password):
    # Create a cursor to execute SQL queries
    cursor = mysql.connection.cursor()

    # Prepare the SELECT query to retrieve the user with the given email
    query = "SELECT * FROM `user` WHERE `email` = %s"
    value = (email,)

    # Execute the query and fetch the results
    cursor.execute(query, value)
    result = cursor.fetchone()

    # Close the cursor
    cursor.close()

    # Check if a user is found and if the password matches
    if result and result[6] == password:
        return True
    else:
        return False
    
@app.route('/index',  methods=['GET', 'POST'])
def index (): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', booking=data)

@app.route('/index_admin',  methods=['GET', 'POST'])
def index_admin ():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking")
    data = cur.fetchall()
    cur.close()

    cur2 = mysql.connection.cursor()
    query2 = "SELECT SUM(price) AS total_sales FROM booking"
    cur2.execute(query2)
    row = cur2.fetchone()
    total_sales = row[0] if row else 'N/A'
    cur2.close()

    cur3= mysql.connection.cursor()
    today = date.today()
    query3 = "SELECT SUM(price) AS today_sales FROM booking WHERE DATE(date) = %s"
    cur3.execute(query3, (today,))
    row = cur3.fetchone()
    today_sales = row[0] if row else '0'
    cur3.close()

    
    return render_template('index_admin.html', booking=data, total_sales=total_sales, today_sales=today_sales) 

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        # Retrieve the values from the submitted form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        area_code = request.form.get('area_code')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Save the new user to the database
        save_user_mysql(first_name, last_name, birthday, email, area_code, phone, password)

        return redirect(url_for('login'))

    # If the request method is GET, simply render the signup.html template
    return render_template('signup.html')
   
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')

#         # Check if the email and password match a user in the database
#         if check_user_credentials(email, password) == True:
#             session['email'] = email
#             return redirect(url_for('index'))  
#         else:
#             flash("Invalid credentials", "warning")
#             return redirect(url_for('index'))

#     return render_template('login-form-5.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email and password match a user in the database
        if email in users and users[email]["password"] == password:
            session['email'] = email
            return redirect(url_for('index'))
        elif email in admins and admins[email]["password"] == password:
            session['email'] = email
            return redirect(url_for('index_admin'))
        else:
            flash("Invalid credentials", "warning")
            return redirect(url_for('login'))

    return render_template('login-form-5.html')

@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        phone = request.form['phone']
        room = request.form['room']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        package = request.form['package']
        price = request.form['price']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO booking (name, phone, room, date, time, duration, package, price) VALUES (%s, %s, %s, %s, %s, %s, %s,  %s)", (name, phone, room, date, time, duration, package,price))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))  

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        room = request.form['room']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        package = request.form['package']
        price = request.form['price']

        cur = mysql.connection.cursor()
        cur.execute(
            """
            UPDATE booking
            SET name=%s, phone=%s, room=%s, date=%s, time=%s, duration=%s, package=%s, price=%s
            WHERE id=%s
            """,
            (name, phone, room, date, time, duration, package, price, id)  # Include 'id' parameter in the tuple
        )
        flash("Data Updated Successfully")
        mysql.connection.commit()
        post = cur.fetchone()
        cur.close()
        return redirect(url_for('index')) 
    
    # Handle GET request (render update form)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking WHERE id=%s", (id,))  # Include 'id' parameter in the tuple
    post = cur.fetchone()
    cur.close()
    return render_template('update.html', post=post)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM booking WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('index')) 

@app.route('/update_admin/<int:id>', methods=['GET', 'POST'])
def update_admin(id):
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        room = request.form['room']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        package = request.form['package']
        price = request.form['price']

        cur = mysql.connection.cursor()
        cur.execute(
            """
            UPDATE booking
            SET name=%s, phone=%s, room=%s, date=%s, time=%s, duration=%s, package=%s, price=%s
            WHERE id=%s
            """,
            (name, phone, room, date, time, duration, package, price, id)  # Include 'id' parameter in the tuple
        )
        flash("Data Updated Successfully")
        mysql.connection.commit()
        post = cur.fetchone()
        cur.close()
        return redirect(url_for('index_admin')) 
    
    # Handle GET request (render update form)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking WHERE id=%s", (id,))  # Include 'id' parameter in the tuple
    post = cur.fetchone()
    cur.close()
    return render_template('update_admin.html', post=post)

@app.route('/delete_admin/<int:id>', methods=['GET', 'POST'])
def delet_admin(id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM booking WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('index_admin')) 

@app.route('/data')
def get_data():
    cursor = mysql.connection.cursor()

    # Execute SQL query to retrieve sales data for June
    query = """
        SELECT MONTH(date) AS month, SUM(price) AS total_sales
        FROM booking 
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY YEAR(date), MONTH(date);
    """

    cursor.execute(query)

    # Fetch all rows of the result set
    result = cursor.fetchall()

    # Process the retrieved data
    data = []
    for row in result:
        data.append({
            'label': row[0],
            'value': row[1]})  # Assuming there is a single column returned, extract the value

    print(data)
    # Return data as JSON
    return jsonify(data) 

@app.route('/dailydata')
def get_daily_data():
    cursor = mysql.connection.cursor()

    # Execute SQL query to retrieve sales data for June
    query = """
       SELECT DAY(date) AS day, SUM(price) AS total_sales 
        FROM booking WHERE MONTH(date) = 7
        GROUP BY MONTH(date), DAY(date)
        ORDER BY MONTH(date), DAY(date)
    """

    cursor.execute(query)

    # Fetch all rows of the result set
    result = cursor.fetchall()

    # Process the retrieved data
    data = []
    for row in result:
        data.append({
            'label': row[0],
            'value': row[1]})  # Assuming there is a single column returned, extract the value

    print(data)
    # Return data as JSON
    return jsonify(data) 

@app.route('/chart',  methods=['GET', 'POST'])
def chart (): 
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM booking")
    # data = cur.fetchall()
    # cur.close()
    return render_template('chart.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
