from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "my_secret_key"

conn = sqlite3.connect('student_management.db',check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        marks BLOB
    )
''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM teachers WHERE username=? AND password=?', (username, password))
        teacher = c.fetchone()

        # c.execute('SELECT * FROM teachers WHERE username=? AND password=?', (username, password))
        # teacher = c.fetchone()


        if teacher:
            session['username'] = username
            return redirect('/teacher_dashboard')
        else:
            return render_template('teacher_login.html', error='Invalid credentials')

    return render_template('teacher_login.html', error=None)

@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM teachers WHERE username=?', (username,))
        existing_teacher = c.fetchone()

        if existing_teacher:
            return render_template('teacher_register.html', error='Username already exists')

        c.execute('INSERT INTO teachers (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        session['username'] = username
        return redirect('/teacher_dashboard')

    return render_template('teacher_register.html', error=None)


@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' in session:
        c.execute('SELECT * FROM students')
        students = c.fetchall()
        num_students = len(students)
        return render_template('teacher_dashboard.html', username=session['username'], num_students=num_students, students=students)
    else:
        return redirect('/teacher_login')

@app.route('/edit_marks/<int:student_id>', methods=['GET', 'POST'])
def edit_marks(student_id):
    if 'username' in session:
        if request.method == 'POST':
            marks = {}
            for key, value in request.form.items():
                if key != 'submit':
                    marks[key] = int(value)

            c.execute('UPDATE students SET marks=? WHERE id=?', (str(marks), student_id))
            conn.commit()
            return redirect('/teacher_dashboard')

        c.execute('SELECT * FROM students WHERE id=?', (student_id,))
        student = c.fetchone()

        if student:
            marks = eval(student[3]) if student[3] else {}
            return render_template('edit_marks.html', username=student[1], marks=marks, student_id=student_id)
        else:
            return redirect('/teacher_dashboard')
    else:
        return redirect('/teacher_login')

    if request.method == 'POST':
        marks = {}
        for key, value in request.form.items():
            if key != 'submit':
                marks[key] = int(value)

        c.execute('UPDATE students SET marks=? WHERE id=?', (str(marks), student_id))
        conn.commit()
        return redirect('/teacher_dashboard')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM students WHERE username=? AND password=?', (username, password))
        student = c.fetchone()

        if student:
            session['username'] = username
            return redirect('/student_dashboard')
        else:
            return render_template('student_login.html', error='Invalid credentials')

    return render_template('student_login.html', error=None)

@app.route('/student_dashboard')
def student_dashboard():
    if 'username' in session:
        c.execute('SELECT * FROM students WHERE username=?', (session['username'],))
        student = c.fetchone()

        if student:
            marks = eval(student[3]) if student[3] else {}
            return render_template('student_dashboard.html', username=session['username'], marks=marks)
        else:
            return redirect('/')
    else:
        return redirect('/student_login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c.execute('SELECT * FROM students WHERE username=?', (username,))
        existing_student = c.fetchone()

        if existing_student:
            return render_template('register.html', error='Username already exists')

        c.execute('INSERT INTO students (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        session['username'] = username
        return redirect('/student_dashboard')

    return render_template('register.html', error=None)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/coming')
def coming():
    return render_template('comingsoon.html')

if __name__ == '__main__':
    app.run(debug=True)
