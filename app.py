from flask import Flask, render_template, request, redirect, session
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "my_secret_key"

conn = sqlite3.connect('student_management.db',check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        class INTEGER NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        class INTEGER NOT NULL,
        marks BLOB
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        student_id INTEGER NOT NULL,
        status INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id)
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
        class_name = request.form['class']

        c.execute('SELECT * FROM teachers WHERE username=?', (username,))
        existing_teacher = c.fetchone()

        if existing_teacher:
            return render_template('teacher_register.html', error='Username already exists')

        c.execute('INSERT INTO teachers (username, password, class) VALUES (?, ?, ?)', (username, password, class_name))
        conn.commit()
        session['username'] = username
        return redirect('/teacher_dashboard')

    return render_template('teacher_register.html', error=None)

@app.route('/manage_attendance', methods=['GET', 'POST'])
def manage_attendance():
    if 'username' in session:
        if request.method == 'POST':
            date = request.form['date']
            student_attendance = request.form.getlist('attendance')

            c.execute('SELECT * FROM teachers WHERE username=?', (session['username'],))
            teacher = c.fetchone()

            if teacher:
                teacher_class = teacher[3]  

                c.execute('SELECT * FROM students WHERE class=?', (teacher_class,))
                students = c.fetchall()

                for student in students:
                    student_id = student[0]
                    if str(student_id) in student_attendance:
                        
                        c.execute('SELECT * FROM attendance WHERE date=? AND student_id=?', (date, student_id))
                        existing_record = c.fetchone()

                        if existing_record:
                            
                            c.execute('UPDATE attendance SET status=? WHERE id=?', ('present', existing_record[0]))
                        else:
                            
                            c.execute('INSERT INTO attendance (date, student_id, status) VALUES (?, ?, ?)',
                                      (date, student_id, 'present'))
                    else:
                        
                        c.execute('SELECT * FROM attendance WHERE date=? AND student_id=?', (date, student_id))
                        existing_record = c.fetchone()

                        if existing_record:
                            
                            c.execute('UPDATE attendance SET status=? WHERE id=?', ('absent', existing_record[0]))
                        else:
                            
                            c.execute('INSERT INTO attendance (date, student_id, status) VALUES (?, ?, ?)',
                                      (date, student_id, 'absent'))

                conn.commit()
                return redirect('/teacher_dashboard')

        c.execute('SELECT * FROM teachers WHERE username=?', (session['username'],))
        teacher = c.fetchone()

        if teacher:
            teacher_class = teacher[3]

            c.execute('SELECT * FROM students WHERE class=?', (teacher_class,))
            students = c.fetchall()

            return render_template('manage_attendance.html', students=students)

    return redirect('/teacher_login')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' in session:
        username = session['username']
        c.execute('SELECT * FROM teachers WHERE username=?', (username,))
        teacher = c.fetchone()

        if teacher:
            teacher_class = teacher[3]
            c.execute('SELECT * FROM students WHERE class=?', (teacher_class,))
            teacher_students = c.fetchall()
            num_students = len(teacher_students)
            return render_template('teacher_dashboard.html', username=username, num_students=num_students, students=teacher_students,teacher_class=teacher_class)
        else:
            return redirect('/teacher_login')
    else:
        return redirect('/teacher_login')

@app.route('/view_attendance')
def view_attendance():
    if 'username' in session:
        username = session['username']
        c.execute('SELECT * FROM students WHERE username=?', (username,))
        student = c.fetchone()

        if student:
            student_id = student[0]
            c.execute('SELECT * FROM attendance WHERE student_id=?', (student_id,))
            attendance_records = c.fetchall()

            return render_template('view_attendance.html', username=username, attendance_records=attendance_records)
    return redirect('/student_login')


@app.route('/edit_marks/<int:student_id>', methods=['GET', 'POST'])
def edit_marks(student_id):
    if 'username' in session:
        if request.method == 'POST':
            marks = {}
            for key, value in request.form.items():
                if key != 'submit':
                    marks[key] = int(value)

            c.execute('UPDATE students SET marks=? WHERE id=?', (json.dumps(marks), student_id))
            conn.commit()
            return redirect('/teacher_dashboard')

        c.execute('SELECT * FROM students WHERE id=?', (student_id,))
        student = c.fetchone()

        if student:
            marks_json = student[4] 
            marks = json.loads(marks_json) if marks_json else {}
            return render_template('edit_marks.html', username=student[1], marks=marks, student_id=student_id)
        else:
            return redirect('/teacher_dashboard')
    else:
        return redirect('/teacher_login')


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
        username = session['username']
        c.execute('SELECT * FROM students WHERE username=?', (username,))
        student = c.fetchone()

        if student:
            marks_json = student[4]  
            marks = json.loads(marks_json) if marks_json else {}
            class_name = student[3] 
            return render_template('student_dashboard.html', username=username, marks=marks, class_name=class_name)
        else:
            return redirect('/')
    else:
        return redirect('/student_login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        class_name = request.form['class']
        c.execute('SELECT * FROM students WHERE username=?', (username,))
        existing_student = c.fetchone()

        if existing_student:
            return render_template('register.html', error='Username already exists')

        c.execute('INSERT INTO students (username, password,class) VALUES (?, ?, ?)', (username, password,class_name))
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

