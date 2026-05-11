from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import os
from dotenv import load_dotenv
import re
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'replace_this_with_a_random_secret_key')

# MySQL configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3307))
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'digital_carbon_tracker')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

EMISSION_FACTORS = {
    'instagram': 80,
    'whatsapp': 3,
    'youtube': 95,
    'netflix': 120,
    'gmail': 4,
    'drive': 2,
    'spotify': 55,
    'zoom': 90
}

THRESHOLDS = {
    'instagram': 2,
    'youtube': 3,
    'netflix': 2,
    'gmail': 30,
    'drive': 10,
    'spotify': 3,
    'zoom': 2
}

ALERT_THRESHOLDS = {
    'instagram': {'threshold': 3, 'unit': 'hours', 'label': 'Instagram'},
    'youtube': {'threshold': 4, 'unit': 'hours', 'label': 'YouTube'},
    'netflix': {'threshold': 2, 'unit': 'hours', 'label': 'Netflix'}
}

POSITIVE_ALERTS = [
    'Great job! Your latest usage is within healthy limits.',
    'Keep up the eco-conscious behavior and aim for lower screen time.',
    'Your usage is balanced today — that helps reduce carbon emissions.'
]

ECO_TIPS = [
    'Switch off apps when you are not actively using them.',
    'Reuse devices longer and choose energy-efficient hardware.',
    'Limit video quality while streaming to save carbon.',
    'Compress files before uploading to cloud storage.',
    'Schedule fewer unnecessary meetings and keep them short.'
]


def require_login():
    if 'loggedin' not in session:
        return redirect(url_for('login'))


def calculate_co2(data):
    total = 0
    contributions = {}
    for key, value in data.items():
        if key in EMISSION_FACTORS:
            contributions[key] = round(value * EMISSION_FACTORS[key], 2)
            total += contributions[key]
    return total, contributions


def calculate_total_usage_hours(usage_data):
    total_hours = 0.0
    for key, amount in usage_data.items():
        value = float(amount or 0)
        if key in ['instagram', 'whatsapp', 'youtube', 'netflix', 'drive', 'spotify', 'zoom']:
            total_hours += value
        elif key == 'gmail':
            total_hours += value / 10.0
        else:
            total_hours += value * 0.2
    return round(total_hours, 2)


def calculate_eco_score(total_usage_hours):
    return max(0, round(100 - total_usage_hours, 2))


def generate_usage_alerts(latest_usage):
    alerts = []
    timestamp = datetime.datetime.now()
    for key, rule in ALERT_THRESHOLDS.items():
        current_value = float(latest_usage.get(key, 0) or 0)
        if current_value > rule['threshold']:
            alerts.append({
                'message': f"{rule['label']} usage is high: {current_value} {rule['unit']} today. Try reducing screen time to lower your carbon footprint.",
                'level': 'warning',
                'created_at': timestamp
            })

    if not latest_usage:
        return [{
            'message': 'No recent app usage found yet. Submit your usage to receive smart alerts and eco-friendly recommendations.',
            'level': 'info',
            'created_at': timestamp
        }]

    if not alerts:
        alerts.append({
            'message': POSITIVE_ALERTS[timestamp.day % len(POSITIVE_ALERTS)],
            'level': 'success',
            'created_at': timestamp
        })

    return alerts


def get_latest_usage_for_user(user_id):
    usage_date_col = get_table_column('app_usage', ['usage_date', 'date'])
    if not table_exists('app_usage') or not table_exists('app_usage_detail') or not table_exists('apps'):
        return {}

    cursor = mysql.connection.cursor()
    cursor.execute(
        f"SELECT au.{usage_date_col} AS usage_date, a.app_key, d.usage_amount "
        "FROM app_usage au "
        "JOIN app_usage_detail d ON d.app_usage_id = au.id "
        "JOIN apps a ON a.id = d.app_id "
        "WHERE au.user_id = %s "
        f"ORDER BY au.{usage_date_col} DESC, au.id DESC "
        "LIMIT 50",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return {}

    latest_date = rows[0]['usage_date']
    latest_usage = {}
    for row in rows:
        if row['usage_date'] != latest_date:
            break
        latest_usage[row['app_key']] = float(row['usage_amount'] or 0)

    return latest_usage

schema_column_cache = {}

def get_table_columns(table_name):
    cache_key = ('columns', table_name)
    if cache_key in schema_column_cache:
        return schema_column_cache[cache_key]

    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s',
        (app.config['MYSQL_DB'], table_name)
    )
    columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
    cursor.close()
    schema_column_cache[cache_key] = columns
    return columns


def get_table_column(table_name, candidates):
    cache_key = (table_name, tuple(candidates))
    if cache_key in schema_column_cache:
        return schema_column_cache[cache_key]

    columns = get_table_columns(table_name)

    for candidate in candidates:
        if candidate in columns:
            schema_column_cache[cache_key] = candidate
            return candidate

    schema_column_cache[cache_key] = candidates[0]
    return candidates[0]


def column_exists(table_name, column_name):
    return column_name in get_table_columns(table_name)


def table_exists(table_name):
    cache_key = ('exists', table_name)
    if cache_key in schema_column_cache:
        return schema_column_cache[cache_key]

    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT COUNT(*) AS count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s',
        (app.config['MYSQL_DB'], table_name)
    )
    exists = cursor.fetchone()['count'] > 0
    cursor.close()
    schema_column_cache[cache_key] = exists
    return exists


def gather_dashboard_data(user_id):
    cursor = mysql.connection.cursor()
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)

    report_date_col = get_table_column('carbon_reports', ['report_date', 'date'])
    usage_date_col = get_table_column('app_usage', ['usage_date', 'date'])

    cursor.execute(
        f"SELECT COALESCE(SUM(total_co2),0) AS daily_total FROM carbon_reports WHERE user_id=%s AND {report_date_col}=%s",
        (user_id, today)
    )
    daily = cursor.fetchone()['daily_total']

    cursor.execute(
        f"SELECT COALESCE(SUM(total_co2),0) AS weekly_total FROM carbon_reports WHERE user_id=%s AND {report_date_col} BETWEEN %s AND %s",
        (user_id, week_ago, today)
    )
    weekly = cursor.fetchone()['weekly_total']

    cursor.execute(
        f"SELECT COALESCE(SUM(total_co2),0) AS monthly_total FROM carbon_reports WHERE user_id=%s AND {report_date_col} BETWEEN %s AND %s",
        (user_id, month_ago, today)
    )
    monthly = cursor.fetchone()['monthly_total']

    cursor.execute(
        f"SELECT * FROM app_usage WHERE user_id=%s ORDER BY {usage_date_col} DESC LIMIT 7",
        (user_id,)
    )
    recent_usage = cursor.fetchall()

    cursor.execute(
        f"SELECT * FROM app_usage WHERE user_id=%s AND {usage_date_col} BETWEEN %s AND %s ORDER BY {usage_date_col} ASC",
        (user_id, month_ago, today)
    )
    month_usage = cursor.fetchall()

    cursor.execute(
        f"SELECT * FROM carbon_reports WHERE user_id=%s ORDER BY {report_date_col} DESC LIMIT 1",
        (user_id,)
    )
    latest_report = cursor.fetchone()

    if table_exists('app_usage_detail') and table_exists('apps'):
        cursor.execute(
            """
            SELECT
                u.id,
                u.username,
                COALESCE(SUM(
                    CASE
                        WHEN a.unit_label = 'hours' THEN d.usage_amount
                        WHEN a.unit_label = 'emails' THEN d.usage_amount / 10
                        WHEN a.unit_label LIKE '%GB%' THEN d.usage_amount / 5
                        ELSE d.usage_amount * 0.2
                    END
                ), 0) AS total_usage_hours
            FROM users u
            LEFT JOIN app_usage au ON au.user_id = u.id
            LEFT JOIN app_usage_detail d ON d.app_usage_id = au.id
            LEFT JOIN apps a ON a.id = d.app_id
            GROUP BY u.id, u.username
            """
        )
        leaderboard_rows = cursor.fetchall()
        leaderboard = []
        for row in leaderboard_rows:
            usage_hours = round(float(row['total_usage_hours'] or 0), 2)
            eco_score = calculate_eco_score(usage_hours)
            leaderboard.append({
                'username': row['username'],
                'usage_hours': usage_hours,
                'eco_score': eco_score
            })
        leaderboard.sort(key=lambda item: item['eco_score'], reverse=True)
    else:
        cursor.execute(
            "SELECT username FROM users ORDER BY username ASC LIMIT 5"
        )
        leaderboard = [
            {
                'username': row['username'],
                'usage_hours': 0.0,
                'eco_score': calculate_eco_score(0.0)
            }
            for row in cursor.fetchall()
        ]

    latest_usage = get_latest_usage_for_user(user_id)
    notifications = generate_usage_alerts(latest_usage)
    current_green_score = calculate_eco_score(calculate_total_usage_hours(latest_usage))
    cursor.close()

    return {
        'daily': round(daily, 2),
        'weekly': round(weekly, 2),
        'monthly': round(monthly, 2),
        'recent_usage': recent_usage,
        'month_usage': month_usage,
        'latest_report': latest_report,
        'leaderboard': leaderboard,
        'notifications': notifications,
        'current_green_score': current_green_score
    }


@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            flash('An account already exists with that email.', 'danger')
            cursor.close()
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, green_score, joined_at) VALUES (%s, %s, %s, %s, %s)',
            (username, email, password_hash, 100, datetime.date.today())
        )
        mysql.connection.commit()
        cursor.close()

        flash('Your account has been created successfully. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password_hash'], password):
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('forgot_password.html')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            flash('If this email exists, a password reset link has been sent. (Email service not configured yet)', 'info')
        else:
            flash('If this email exists, a password reset link has been sent. (Email service not configured yet)', 'info')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')


@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_summary = gather_dashboard_data(user_id)
    usage_date_col = get_table_column('app_usage', ['usage_date', 'date'])
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    labels = []
    totals = []
    usage_hours = []
    weekly_labels = []
    weekly_totals = []
    monthly_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    monthly_totals = [0, 0, 0, 0]
    pie_labels = []
    pie_values = []
    top_contributor = None

    if user_summary['recent_usage']:
        for entry in reversed(user_summary['recent_usage']):
            labels.append(entry[usage_date_col].strftime('%b %d'))
            totals.append(float(entry['total_co2']))
            if table_exists('app_usage_detail'):
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT COALESCE(SUM(usage_amount),0) AS total_usage FROM app_usage_detail WHERE app_usage_id=%s', (entry['id'],))
                usage_hours.append(float(cursor.fetchone()['total_usage'] or 0))
                cursor.close()
            else:
                usage_hours.append(0.0)

        latest_usage = user_summary['recent_usage'][0]
        if table_exists('apps') and table_exists('app_usage_detail'):
            cursor = mysql.connection.cursor()
            cursor.execute(
                'SELECT a.app_key, d.usage_amount, d.co2_value FROM app_usage_detail d JOIN apps a ON a.id = d.app_id WHERE d.app_usage_id = %s',
                (latest_usage['id'],)
            )
            latest_details = cursor.fetchall()
            cursor.close()

            contributions = {
                row['app_key'].capitalize(): float(row['co2_value']) for row in latest_details
            }
            pie_labels = list(contributions.keys())
            pie_values = [round(val, 2) for val in contributions.values()]
            if contributions:
                top_contributor = max(contributions, key=contributions.get)
        else:
            top_contributor = 'Awaiting usage'

    if user_summary['month_usage']:
        recent_month = user_summary['month_usage'][-7:]
        for entry in recent_month:
            weekly_labels.append(entry[usage_date_col].strftime('%b %d'))
            weekly_totals.append(float(entry['total_co2']))
        month_ago = datetime.date.today() - datetime.timedelta(days=30)
        for entry in user_summary['month_usage']:
            idx = min((entry[usage_date_col] - month_ago).days // 7, 3)
            monthly_totals[idx] += float(entry['total_co2'])
        monthly_totals = [round(value, 2) for value in monthly_totals]

    initials = ''.join([segment[0].upper() for segment in user['username'].split() if segment])[:2]
    return render_template(
        'dashboard.html',
        username=session['username'],
        logged_in_email=user['email'],
        avatar_initials=initials,
        profile_picture=None,
        daily_total=user_summary['daily'],
        weekly_total=user_summary['weekly'],
        monthly_total=user_summary['monthly'],
        green_score=user_summary['current_green_score'],
        eco_tip=ECO_TIPS[datetime.date.today().day % len(ECO_TIPS)],
        leaderboard=user_summary['leaderboard'],
        notifications=user_summary['notifications'],
        latest_report=user_summary['latest_report'],
        chart_labels=labels,
        chart_totals=totals,
        chart_usage=usage_hours,
        pie_labels=pie_labels,
        pie_values=pie_values,
        weekly_labels=weekly_labels,
        weekly_values=weekly_totals,
        monthly_labels=monthly_labels,
        monthly_values=monthly_totals,
        top_contributor=top_contributor
    )


@app.route('/submit-usage', methods=['POST'])
def submit_usage():
    if 'loggedin' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    user_id = session['user_id']
    date = datetime.date.today()
    instagram = float(request.form.get('instagram', 0))
    whatsapp = float(request.form.get('whatsapp', 0))
    youtube = float(request.form.get('youtube', 0))
    netflix = float(request.form.get('netflix', 0))
    gmail = int(request.form.get('gmail', 0))
    drive = float(request.form.get('drive', 0))
    spotify = float(request.form.get('spotify', 0))
    zoom = float(request.form.get('zoom', 0))
    cursor = None

    usage_data = {
        'instagram': instagram,
        'whatsapp': whatsapp,
        'youtube': youtube,
        'netflix': netflix,
        'gmail': gmail,
        'drive': drive,
        'spotify': spotify,
        'zoom': zoom
    }

    total_co2, contributions = calculate_co2(usage_data)

    try:
        cursor = mysql.connection.cursor()
        usage_date_col = get_table_column('app_usage', ['usage_date', 'date'])
        report_date_col = get_table_column('carbon_reports', ['report_date', 'date'])

        # Ensure apps table exists and has data
        if not table_exists('apps'):
            cursor.execute('''CREATE TABLE apps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_key VARCHAR(50) NOT NULL UNIQUE,
                app_name VARCHAR(100) NOT NULL,
                unit_label VARCHAR(50) NOT NULL,
                emission_factor DECIMAL(6,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB''')
            apps_data = [
                ('instagram', 'Instagram', 'hours', 80),
                ('whatsapp', 'WhatsApp', 'hours', 3),
                ('youtube', 'YouTube', 'hours', 95),
                ('netflix', 'Netflix', 'hours', 120),
                ('gmail', 'Gmail', 'emails', 4),
                ('drive', 'Google Drive', 'hours', 2),
                ('spotify', 'Spotify', 'hours', 55),
                ('zoom', 'Zoom', 'hours', 90)
            ]
            for app_key, app_name, unit_label, factor in apps_data:
                cursor.execute('INSERT INTO apps (app_key, app_name, unit_label, emission_factor) VALUES (%s, %s, %s, %s)', (app_key, app_name, unit_label, factor))

        # Ensure app_usage_detail table exists
        if not table_exists('app_usage_detail'):
            cursor.execute('''CREATE TABLE app_usage_detail (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_usage_id INT NOT NULL,
                app_id INT NOT NULL,
                usage_amount DECIMAL(8,2) NOT NULL,
                co2_value DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_usage_id) REFERENCES app_usage(id) ON DELETE CASCADE,
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''')

        cursor.execute(
            f'INSERT INTO app_usage (user_id, {usage_date_col}, total_co2) VALUES (%s, %s, %s)',
            (user_id, date, total_co2)
        )
        app_usage_id = cursor.lastrowid

        write_details = table_exists('apps') and table_exists('app_usage_detail')
        if write_details:
            cursor.execute('SELECT id, app_key FROM apps')
            apps = {row['app_key']: row['id'] for row in cursor.fetchall()}
            for key, amount in usage_data.items():
                if amount <= 0:
                    continue
                app_id = apps.get(key)
                if app_id is None:
                    continue
                cursor.execute(
                    'INSERT INTO app_usage_detail (app_usage_id, app_id, usage_amount, co2_value) VALUES (%s, %s, %s, %s)',
                    (app_usage_id, app_id, amount, round(contributions[key], 2))
                )

        week_ago = date - datetime.timedelta(days=7)
        month_ago = date - datetime.timedelta(days=30)

        cursor.execute(
            f'SELECT COALESCE(SUM(total_co2),0) AS weekly_total FROM app_usage WHERE user_id=%s AND {usage_date_col} BETWEEN %s AND %s',
            (user_id, week_ago, date)
        )
        weekly_total = cursor.fetchone()['weekly_total']

        cursor.execute(
            f'SELECT COALESCE(SUM(total_co2),0) AS monthly_total FROM app_usage WHERE user_id=%s AND {usage_date_col} BETWEEN %s AND %s',
            (user_id, month_ago, date)
        )
        month_total = cursor.fetchone()['monthly_total']

        report_columns = ['user_id', report_date_col, 'total_co2']
        report_values = [user_id, date, total_co2]
        if column_exists('carbon_reports', 'daily_co2'):
            report_columns.append('daily_co2')
            report_values.append(total_co2)
        if column_exists('carbon_reports', 'weekly_co2'):
            report_columns.append('weekly_co2')
            report_values.append(weekly_total)
        if column_exists('carbon_reports', 'monthly_co2'):
            report_columns.append('monthly_co2')
            report_values.append(month_total)

        placeholders = ', '.join(['%s'] * len(report_values))
        cursor.execute(
            f'INSERT INTO carbon_reports ({", ".join(report_columns)}) VALUES ({placeholders})',
            tuple(report_values)
        )

        total_usage_hours = calculate_total_usage_hours(usage_data)
        green_score = calculate_eco_score(total_usage_hours)
        cursor.execute('UPDATE users SET green_score = %s WHERE id = %s', (green_score, user_id))

        latest_usage = get_latest_usage_for_user(user_id)
        notification_list = generate_usage_alerts(latest_usage)

        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()

        response = {
            'status': 'success',
            'message': 'Usage data logged successfully.',
            'total_co2': round(total_co2, 2),
            'contributions': contributions,
            'weekly_total': round(weekly_total, 2),
            'monthly_total': round(month_total, 2),
            'green_score': green_score,
            'notifications': notification_list,
            'eco_tip': ECO_TIPS[datetime.date.today().day % len(ECO_TIPS)],
            'details_written': write_details
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        if cursor:
            cursor.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/report')
def report():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    data = gather_dashboard_data(user_id)
    return render_template('report.html', username=session['username'], latest_report=data['latest_report'], eco_tip=ECO_TIPS[datetime.date.today().day % len(ECO_TIPS)])


@app.route('/download-report')
def download_report():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    report_date_col = get_table_column('carbon_reports', ['report_date', 'date'])
    cursor.execute(f'SELECT * FROM carbon_reports WHERE user_id = %s ORDER BY {report_date_col} DESC LIMIT 1', (user_id,))
    report = cursor.fetchone()
    cursor.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle('Digital Carbon Tracker Report')
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(50, 740, 'AI Digital Carbon Tracker - Carbon Report')
    pdf.setFont('Helvetica', 12)
    pdf.drawString(50, 710, f'User: {user["username"]}')
    pdf.drawString(50, 690, f'Email: {user["email"]}')
    report_date_key = 'report_date' if 'report_date' in report else 'date'
    pdf.drawString(50, 670, f'Date: {report[report_date_key]}')
    pdf.drawString(50, 640, f'Daily Carbon Emissions: {report["daily_co2"]} g CO2')
    pdf.drawString(50, 620, f'Weekly Carbon Emissions: {report["weekly_co2"]} g CO2')
    pdf.drawString(50, 600, f'Monthly Carbon Emissions: {report["monthly_co2"]} g CO2')
    pdf.drawString(50, 580, f'Total Carbon Footprint: {report["total_co2"]} g CO2')
    pdf.drawString(50, 560, f'Green Score: {user["green_score"]} / 100')
    pdf.drawString(50, 530, 'Eco Tip: ' + ECO_TIPS[datetime.date.today().day % len(ECO_TIPS)])
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='carbon_report.pdf', mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)
