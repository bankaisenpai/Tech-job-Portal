import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
from sc import scrape_jobs

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# --- DB Utility ---
def db_conn():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# --- Decorator for login check ---
def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*a, **kw)
    return wrapper

# --- Routes ---
@app.route('/')
def landing():
    return redirect(url_for('index')) if 'user_id' in session else render_template('landing.html')

@app.route('/search-page')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {k: request.form.get(k, '').strip() for k in ['username', 'email', 'password', 'confirm_password']}
        if not all(data.values()):
            flash('All fields are required!', 'error')
        elif data['password'] != data['confirm_password']:
            flash('Passwords do not match!', 'error')
        elif len(data['password']) < 6:
            flash('Password must be at least 6 characters!', 'error')
        else:
            conn, cur = db_conn(), None
            try:
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM users WHERE username=%s OR email=%s", (data['username'], data['email']))
                if cur.fetchone():
                    flash('Username or email exists!', 'error')
                else:
                    cur.execute("INSERT INTO users (username,email,password_hash) VALUES (%s,%s,%s)",
                                (data['username'], data['email'], generate_password_hash(data['password'])))
                    conn.commit()
                    flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('login'))
            finally:
                if cur: cur.close()
                conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form.get('username', '').strip(), request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password required!', 'error')
        else:
            conn = db_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
            cur.close(); conn.close()
            if user and check_password_hash(user['password_hash'], password):
                session.update({'user_id': user['id'], 'username': user['username']})
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('index'))
            flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('landing'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    role, location = request.form.get('job_role', '').strip(), request.form.get('location', '').strip()
    job_type = request.form.get('job_type', '')
    if not role or not location:
        flash('Please enter both role and location', 'error')
        return redirect(url_for('index'))

    scrape_jobs(role, location)
    query = """SELECT Source, Job_Title, Company, Location, Job_Type, Salary, Posted,
                      Job_Summary, Benefits, Job_Link, id FROM jobs WHERE 1"""
    params = []
    if job_type:
        query += " AND Job_Type LIKE %s"
        params.append(f"%{job_type}%")
    query += " ORDER BY id DESC LIMIT 20"

    conn = db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params)
    jobs = cur.fetchall()
    cur.close(); conn.close()

    if job_type and not jobs:
        flash(f'No {job_type} jobs found for "{role}" in "{location}".', 'warning')

    return render_template('results.html', jobs=jobs, role=role, location=location, job_type_filter=job_type)

@app.route('/save_job/<int:job_id>')
@login_required
def save_job(job_id):
    conn = db_conn(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM saved_jobs WHERE user_id=%s AND job_id=%s", (session['user_id'], job_id))
    if cur.fetchone():
        flash('Job already saved!', 'info')
    else:
        cur.execute("INSERT INTO saved_jobs (user_id, job_id) VALUES (%s, %s)", (session['user_id'], job_id))
        conn.commit()
        flash('Job saved successfully!', 'success')
    cur.close(); conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/unsave_job/<int:job_id>')
@login_required
def unsave_job(job_id):
    conn = db_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM saved_jobs WHERE user_id=%s AND job_id=%s", (session['user_id'], job_id))
    conn.commit(); cur.close(); conn.close()
    flash('Job removed from saved list!', 'success')
    return redirect(request.referrer or url_for('saved_jobs'))

@app.route('/saved_jobs')
@login_required
def saved_jobs():
    conn = db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT j.*, sj.saved_at FROM jobs j
                   JOIN saved_jobs sj ON j.id=sj.job_id
                   WHERE sj.user_id=%s ORDER BY sj.saved_at DESC""", (session['user_id'],))
    jobs = cur.fetchall()
    cur.close(); conn.close()
    return render_template('saved_jobs.html', jobs=jobs)

@app.route('/profile')
@login_required
def profile():
    conn = db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute("SELECT COUNT(*) AS count FROM saved_jobs WHERE user_id=%s", (session['user_id'],))
    saved_count = cur.fetchone()['count']
    cur.close(); conn.close()
    return render_template('profile.html', user=user, saved_count=saved_count)

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    conn = db_conn(); cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        job_role, location = request.form.get('job_role', '').strip(), request.form.get('location', '').strip()
        email_alerts = 'email_alerts' in request.form
        cur.execute("""UPDATE users SET preferred_role=%s, preferred_location=%s, email_alerts=%s WHERE id=%s""",
                    (job_role, location, email_alerts, session['user_id']))
        conn.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('profile'))

    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close(); conn.close()
    return render_template('preferences.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
