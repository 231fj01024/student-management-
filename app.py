from flask import Flask, render_template, redirect, url_for, request, g
import sqlite3
from typing import Any

app = Flask(__name__)
DATABASE = 'students.db'

# -----------------------
# DATABASE HELPER FUNCTIONS
# -----------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enables dict-like access
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the students table if not exists."""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL,
                class TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        db.commit()

# -----------------------
# ROUTES
# -----------------------

@app.route('/')
def home():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('index.html', std=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        student_class = request.form['class']
        email = request.form['email']

        db = get_db()
        db.execute('INSERT INTO students (name, roll, class, email) VALUES (?, ?, ?, ?)',
                   (name, roll, student_class, email))
        db.commit()
        return redirect(url_for('home'))

    return render_template('add.html')

@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    db = get_db()
    db.execute('DELETE FROM students WHERE id = ?', (student_id,))
    db.commit()
    return redirect(url_for('home'))

@app.route('/update/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        return "Student not found", 404

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        student_class = request.form['class']
        email = request.form['email']

        db.execute('''
            UPDATE students
            SET name = ?, roll = ?, class = ?, email = ?
            WHERE id = ?
        ''', (name, roll, student_class, email, student_id))
        db.commit()
        return redirect(url_for('home'))

    return render_template('update.html', student=student)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# -----------------------
# MAIN ENTRY POINT
# -----------------------
if __name__ == '__main__':
    init_db()  # Ensure table exists
    app.run(debug=True, use_reloader=False)
