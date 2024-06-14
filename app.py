import os
from flask import Flask, request,render_template,redirect, flash, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

if not os.path.exists('database'):
    os.makedirs('database')

conn = sqlite3.connect('database/conference.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY,
          username TEXT NOT NULL,
          password TEXT NOT NULL,
          email TEXT NOT NULL,
          is_admin INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS registration(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)   
)''')

c.execute('''CREATE TABLE IF NOT EXISTS schedule(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            time TEXT NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS feedback(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            feedback TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS superusercred(
            username TEXT NOT NULL,
            password TEXT NOT NULL
)''')

c.execute('SELECT * FROM superusercred')
conn.commit()
adminuser= c.fetchone()
if not adminuser:
    c.execute("INSERT INTO superusercred VALUES('admin', 'admin')")
    conn.commit()


def user_registration():
    c.execute('SELECT * FROM users')
    conn.commit()
    data = c.fetchall()
    user_registration =[]
    for d in data:
        if str(d[-1])== '0':
            user_registration.append(d)
    return user_registration

def schedule_conf():
    c.execute('SELECT * FROM schedule')
    conn.commit()
    data = c.fetchall()
    schedule_conf =[]
    for d in data:
        schedule_conf.append(d)
    return schedule_conf

conn.commit()
conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('database/conference.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_password, email))
        conn.commit()
        conn.close()
        flash('registration successful.Please login')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('database/conference.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = c.fetchone()
        conn.close()
        if user:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        c.execute('SELECT * FROM superusercred')
        conn.commit()
        superusercred = c.fetchall()
        for i in superusercred:
            if str(i[0]) == str(username) and str(i[1]) == str(password):
                user_registration = user_registration()    
                schedule_conf = schedule_conf()
                l1= len(user_registration)
                l2= len(schedule_conf)  
                return render_template('admin_dashboard.html', user_registration=user_registration, schedule_conf=schedule_conf, l1=l1, l2=l2)
        else:
            return redirect('admin.html',err='Invalid credentials')
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database/conference.db')
    c = conn.cursor()
    c.execute('SELECT * FROM schedule')
    schedules = c.fetchall()
    conn.close()
    return render_template('dashboard.html', schedules=schedules)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback = request.form['feedback']
        conn = sqlite3.connect('database/conference.db')
        c = conn.cursor()
        c.execute('INSERT INTO feedback (user_id, feedback) VALUES (?, ?)', (1, feedback))
        conn.commit()
        conn.close()
        flash('Thank you for your feedback')
        return redirect(url_for('home'))
    return render_template('feedback.html')

@app.route('/schedule')
def schedule():
    conn = sqlite3.connect('database/conference.db')
    c = conn.cursor()
    c.execute('SELECT * FROM schedule')
    schedule = c.fetchall()
    conn.close()
    return render_template('schedule.html', schedule=schedule)

def add_schedule():
    with sqlite3.connect('database/conference.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO schedule (title, description, time) VALUES (?, ?, ?)', ('opening ceremony', 'Welcome speech and introduction', '09:00 AM'))
        c.execute('INSERT INTO schedule (title, description, time) VALUES (?, ?, ?)', ('keynote speech', 'keynotes speech by our guest speaker', '10:00 AM'))
        c.execute('INSERT INTO schedule (title, description, time) VALUES (?, ?, ?)', ('lunch break', 'lunch break', '12:00 PM'))
        conn.commit()

add_schedule()

@app.route('/logout')
def logout():
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
