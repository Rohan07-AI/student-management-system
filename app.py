from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__,
           template_folder='templates',
           static_folder='static')
app.secret_key = "secret123"

# SQLite connection
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    course TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Insert default user
cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    conn.commit()

# ---------------- ROUTES ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search')

    if search:
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM students")

    data = cursor.fetchall()
    return render_template('index.html', students=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        cursor.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )
        conn.commit()

        flash("Student added successfully!", "success")
        return redirect('/')

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()

    flash("Student deleted successfully!", "danger")
    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        cursor.execute(
            "UPDATE students SET name=?, email=?, course=? WHERE id=?",
            (name, email, course, id)
        )
        conn.commit()

        flash("Student updated successfully!", "warning")
        return redirect('/')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    return render_template('edit.html', student=student)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
