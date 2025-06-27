from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from flask import send_file


app = Flask(__name__)
app.secret_key = 'qwerty1234'

# Папка для загрузки файлов
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Инициализация базы
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
    CREATE TABLE IF NOT EXISTS publications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year INTEGER,
        type TEXT,
        status TEXT,
        file_path TEXT,
        comment TEXT,
        updated_at TEXT,
        scopus_status TEXT,
        faculty TEXT,
        language TEXT
    )
''')
        conn.commit()


init_db()


from fpdf import FPDF
from flask import send_file

@app.route('/export/pdf')
def export_pdf():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=9)

    pdf.cell(0, 8, txt="Жарияланымдар есебі", ln=1, align='C')
    pdf.ln(3)

    headers = ['Автор', 'Атауы', 'Түрі', 'Жылы', 'Тілі', 'Статус', 'Scopus/WoS', 'Ескерту', 'Файл атауы']
    col_widths = [30, 50, 25, 15, 20, 25, 30, 45, 45]

    # Заголовки
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT author, title, type, year, language, status, scopus_status, comment, file_path
            FROM publications
        ''')
        rows = c.fetchall()

    total = len(rows)
    accepted = sum(1 for row in rows if row[5] == 'Қабылданды')
    rejected = sum(1 for row in rows if row[5] == 'Қайтарылды')

    for row in rows:
        for i, item in enumerate(row):
            text = str(item) if item else '—'
            if headers[i] == 'Статус':
                if text == 'Қабылданды':
                    pdf.set_fill_color(144, 238, 144)
                elif text == 'Қайтарылды':
                    pdf.set_fill_color(255, 182, 193)
                else:
                    pdf.set_fill_color(255, 255, 224)
                pdf.cell(col_widths[i], 8, text, border=1, align='C', fill=True)
            else:
                pdf.cell(col_widths[i], 8, text, border=1, align='C')
        pdf.ln()

    # Итого в конце
    pdf.ln(3)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 8, f"Барлығы: {total} | Қабылданды: {accepted} | Қайтарылды: {rejected}", ln=1)

    file_path = os.path.join(os.path.dirname(__file__), 'publications.pdf')
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)




def add_missing_columns():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        c.execute("PRAGMA table_info(publications)")
        columns = [col[1] for col in c.fetchall()]

        if 'scopus_status' not in columns:
            c.execute('ALTER TABLE publications ADD COLUMN scopus_status TEXT')

        if 'faculty' not in columns:
            c.execute('ALTER TABLE publications ADD COLUMN faculty TEXT')

        conn.commit()


add_missing_columns()


@app.route('/')
def index():
    query = request.args.get('query', '')
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        if query:
            c.execute('''
                SELECT title, author, year, type, file_path, scopus_status 
                FROM publications 
                WHERE status="Қабылданды" 
                AND (title LIKE ? OR author LIKE ? OR year LIKE ?)
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            c.execute('''
                SELECT title, author, year, type, file_path, scopus_status 
                FROM publications 
                WHERE status="Қабылданды"
            ''')
        publications = [
            {
                'title': row[0],
                'author': row[1],
                'year': row[2],
                'type': row[3],
                'file_path': row[4],
                'scopus_status': row[5]
            } for row in c.fetchall()
        ]
    return render_template('welcome.html', publications=publications)

@app.route('/login-page')
def login_page():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM faculties")
    faculty_count = c.fetchone()[0]

    from datetime import datetime
    current_date = datetime.now().strftime('%d.%m.%Y')

    conn.close()

    return render_template('dashboard.html',
                           
                           faculty_count=faculty_count,
                           current_date=current_date)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']
    if (login == 'admin' and password == '1234') or (login == 'student' and password == '1234'):
        session['role'] = 'admin' if login == 'admin' else 'student'
        session['login'] = login
        return redirect(url_for('dashboard'))
    else:
        return 'Қате логин немесе құпиясөз'

@app.route('/logout')
def logout():
    session.pop('role', None)
    session.pop('login', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        author = session['login']
        year = request.form['year']
        pub_type = request.form['type']
        faculty = request.form['faculty']
        language = request.form['language']

        file = request.files.get('file')
        file_path = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = f"{app.config['UPLOAD_FOLDER']}/{filename}".replace("\\", "/")
            file.save(file_path)

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('''
  INSERT INTO publications (title, author, year, type, status, file_path, faculty, language)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (title, author, year, pub_type, 'Қарастырылуда', file_path, faculty, language))
        
            conn.commit()

        return redirect(url_for('dashboard'))

    return render_template('upload.html')


@app.route('/moderation')
def moderation():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    faculty = request.args.get('faculty', '')
    pub_type = request.args.get('type', '')
    year = request.args.get('year', '')
    language = request.args.get('language', '')  # 👈 добавили обработку языка
    status = request.args.get('status', '')

    query = '''
        SELECT id, title, author, year, type, status, file_path, faculty, language
        FROM publications
        WHERE 1=1
    '''
    params = []

    if faculty:
        query += ' AND faculty LIKE ?'
        params.append(f'%{faculty}%')
    if pub_type:
        query += ' AND type LIKE ?'
        params.append(f'%{pub_type}%')
    if year:
        query += ' AND year = ?'
        params.append(year)
    if language:
        query += ' AND language = ?'  # 👈 фильтр по языку
        params.append(language)
    if status:
        query += ' AND status = ?'
        params.append(status)

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute(query, params)
        publications = c.fetchall()

    return render_template('moderation.html', publications=publications)




@app.route('/approve/<int:id>')
def approve(id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE publications SET status="Қабылданды" WHERE id=?', (id,))
        conn.commit()
    return redirect(url_for('moderation'))

@app.route('/reject/<int:id>')
def reject(id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE publications SET status="Қайтарылды" WHERE id=?', (id,))
        conn.commit()
    return redirect(url_for('moderation'))

@app.route('/stats')
def stats():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        # График по годам
        c.execute("SELECT year, COUNT(*) FROM publications GROUP BY year")
        year_data = c.fetchall()
        year_labels = [str(row[0]) for row in year_data]
        year_counts = [row[1] for row in year_data]

        # График по факультетам
        c.execute("SELECT faculty, COUNT(*) FROM publications GROUP BY faculty")
        faculty_data = c.fetchall()
        faculty_labels = [row[0] if row[0] else '—' for row in faculty_data]
        faculty_counts = [row[1] for row in faculty_data]

        # График по ролям (если есть таблица users)
        try:
            c.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            role_data = c.fetchall()
            role_labels = [row[0] for row in role_data]
            role_counts = [row[1] for row in role_data]
        except sqlite3.OperationalError:
            role_labels = []
            role_counts = []

        # График по типам публикаций
        c.execute("SELECT type, COUNT(*) FROM publications GROUP BY type")
        type_data = c.fetchall()
        type_labels = [row[0] for row in type_data]
        type_counts = [row[1] for row in type_data]

        # График по статусу публикаций
        c.execute("SELECT status, COUNT(*) FROM publications GROUP BY status")
        status_data = c.fetchall()
        status_labels = [row[0] for row in status_data]
        status_counts = [row[1] for row in status_data]

    return render_template('stats.html',
                           year_labels=year_labels,
                           year_counts=year_counts,
                           faculty_labels=faculty_labels,
                           faculty_counts=faculty_counts,
                           role_labels=role_labels,
                           role_counts=role_counts,
                           type_labels=type_labels,
                           type_counts=type_counts,
                           status_labels=status_labels,
                           status_counts=status_counts)



import pandas as pd

@app.route('/export/excel')
def export_excel():
    query = '''
        SELECT 
            author AS "Кім жүктеді",
            title AS "Атауы",
            type AS "Түрі",
            year AS "Жылы",
            language AS "Тілі",
            status AS "Статус",
            author AS "Автор(лар)",
            scopus_status AS "Scopus/WoS статусы",
            comment AS "Ескерту",
            file_path
        FROM publications
    '''

    with sqlite3.connect('database.db') as conn:
        df = pd.read_sql_query(query, conn)

    if df.empty:
        return "Ешқандай мәлімет табылмады."

    # Файл атынан тек имя файла алу
    df['Файл атауы'] = df['file_path'].apply(lambda x: os.path.basename(x) if x else 'Жоқ')

    # Файл пути колонкасын алып тастау
    df.drop(columns=['file_path'], inplace=True)

    file_path = 'exported_publications.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)



@app.route('/messages')
def messages():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    
    author = session['login']
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT title, status, comment, updated_at
            FROM publications
            WHERE author=? AND (comment IS NOT NULL AND comment != '')
        ''', (author,))
        messages = c.fetchall()

    return render_template('messages.html', messages=messages)



@app.route('/my-publications', methods=['GET', 'POST'])
def my_publications():
    if 'role' not in session or session['role'] not in ['student', 'admin']:
        return redirect(url_for('index'))

    author = session['login']
    status_filter = request.args.get('status')
    year_filter = request.args.get('year')

    query = 'SELECT id, title, year, type, status, scopus_status, comment, file_path FROM publications WHERE author=?'
    params = [author]

    if status_filter:
        query += ' AND status=?'
        params.append(status_filter)
    if year_filter:
        query += ' AND year=?'
        params.append(year_filter)

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute(query, params)
        publications = c.fetchall()

    return render_template('my-publications.html', publications=publications)


@app.route('/get-role')
def get_role():
    if 'role' in session:
        return {'role': session['role']}
    return {'role': None}

@app.route('/moderation-action/<int:id>', methods=['POST'])
def moderation_action(id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    action = request.form['action']
    comment = request.form.get('comment', '')
    status = 'Қабылданды' if action == 'approve' else 'Қайтарылды'
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE publications SET status=?, comment=?, updated_at=? WHERE id=?',
                  (status, comment, updated_at, id))
        conn.commit()
    
    return redirect(url_for('moderation'))

from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

from flask import send_from_directory


if __name__ == '__main__':
    app.run(debug=True)
