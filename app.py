from flask import Flask, render_template, request, g
import sqlite3
import random

app = Flask(__name__)
DATABASE = 'syrian_arabic.db'

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS phrases (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            english TEXT NOT NULL,
                            transliteration TEXT NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS verbs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            base_form TEXT NOT NULL,
                            transliteration TEXT NOT NULL,
                            example_sentence TEXT NOT NULL
                        )''')
        db.commit()

# Seed data
def seed_data():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Seed phrases (with 'Feeny')
        cursor.executemany('''INSERT OR IGNORE INTO phrases (english, transliteration)
                              VALUES (?, ?)''', [
            ("Can I go?", "Feeny rah?"),
            ("Should I leave?", "Lazem etrok?"),
            ("I am going.", "Ana rah."),
            ("Where are you?", "Wen enta?"),
            ("I am here.", "Ana hon."),
            ("Can I see?", "Feeny shoof?"),
        ])
        # Seed verbs
        cursor.executemany('''INSERT OR IGNORE INTO verbs (base_form, transliteration, example_sentence)
                              VALUES (?, ?, ?)''', [
            ("to go", "rah", "Ana rah al-madrase (I am going to school)."),
            ("to come", "jeh", "Emta jeye? (When are you coming?)"),
            ("to stay", "dal", "Lazem edal hon (I should stay here)."),
            ("to leave", "etrok", "Lazem etrok al-bait (I should leave the house)."),
            ("to see", "shoof", "Feeny shoof? (Can I see?)"),
        ])
        db.commit()

# Home Page
@app.route('/')
def index():
    db = get_db()
    phrases = db.execute('SELECT * FROM phrases').fetchall()
    return render_template('index.html', phrases=phrases)

# Verbs Page
@app.route('/verbs')
def verbs():
    db = get_db()
    verbs = db.execute('SELECT * FROM verbs').fetchall()
    return render_template('verbs.html', verbs=verbs)

# Alphabet Page
@app.route('/alphabet')
def alphabet():
    letters = [
        {"name": "Alif", "isolated": "ا", "initial": "ـا", "medial": "ـا", "final": "ـا"},
        {"name": "Ba", "isolated": "ب", "initial": "بـ", "medial": "ـبـ", "final": "ـب"},
        {"name": "Ta", "isolated": "ت", "initial": "تـ", "medial": "ـتـ", "final": "ـت"},
        {"name": "Tha", "isolated": "ث", "initial": "ثـ", "medial": "ـثـ", "final": "ـث"},
        {"name": "Jeem", "isolated": "ج", "initial": "جـ", "medial": "ـجـ", "final": "ـج"},
        {"name": "Haa", "isolated": "ح", "initial": "حـ", "medial": "ـحـ", "final": "ـح"},
        {"name": "Khaa", "isolated": "خ", "initial": "خـ", "medial": "ـخـ", "final": "ـخ"},
        {"name": "Dal", "isolated": "د", "initial": "ـد", "medial": "ـد", "final": "ـد"},
        {"name": "Ra", "isolated": "ر", "initial": "ـر", "medial": "ـر", "final": "ـر"},
        {"name": "Zay", "isolated": "ز", "initial": "ـز", "medial": "ـز", "final": "ـز"},
        {"name": "Seen", "isolated": "س", "initial": "سـ", "medial": "ـسـ", "final": "ـس"},
        {"name": "Sheen", "isolated": "ش", "initial": "شـ", "medial": "ـشـ", "final": "ـش"},
        {"name": "Sad", "isolated": "ص", "initial": "صـ", "medial": "ـصـ", "final": "ـص"},
        {"name": "Dad", "isolated": "ض", "initial": "ضـ", "medial": "ـضـ", "final": "ـض"},
        {"name": "Taa", "isolated": "ط", "initial": "طـ", "medial": "ـطـ", "final": "ـط"},
        {"name": "Zaa", "isolated": "ظ", "initial": "ظـ", "medial": "ـظـ", "final": "ـظ"},
        {"name": "Ayn", "isolated": "ع", "initial": "عـ", "medial": "ـعـ", "final": "ـع"},
        {"name": "Ghain", "isolated": "غ", "initial": "غـ", "medial": "ـغـ", "final": "ـغ"},
        {"name": "Faa", "isolated": "ف", "initial": "فـ", "medial": "ـفـ", "final": "ـف"},
        {"name": "Qaaf", "isolated": "ق", "initial": "قـ", "medial": "ـقـ", "final": "ـق"},
        {"name": "Kaaf", "isolated": "ك", "initial": "كـ", "medial": "ـكـ", "final": "ـك"},
        {"name": "Laam", "isolated": "ل", "initial": "لـ", "medial": "ـلـ", "final": "ـل"},
        {"name": "Meem", "isolated": "م", "initial": "مـ", "medial": "ـمـ", "final": "ـم"},
        {"name": "Noon", "isolated": "ن", "initial": "نـ", "medial": "ـنـ", "final": "ـن"},
        {"name": "Ha", "isolated": "هـ", "initial": "هـ", "medial": "ـهـ", "final": "ـه"},
        {"name": "Waw", "isolated": "و", "initial": "ـو", "medial": "ـو", "final": "ـو"},
        {"name": "Yaa", "isolated": "ي", "initial": "يـ", "medial": "ـيـ", "final": "ـي"},
    ]
    return render_template('alphabet.html', letters=letters)

# Multiple Choice Quiz
@app.route('/quiz-mc', methods=['GET', 'POST'])
def quiz_mc():
    db = get_db()
    all_phrases = db.execute('SELECT * FROM phrases').fetchall()

    if request.method == 'POST':
        score = 0
        for phrase_id, user_answer in request.form.items():
            correct_answer = db.execute('SELECT transliteration FROM phrases WHERE id = ?', (phrase_id,)).fetchone()
            if correct_answer and user_answer == correct_answer['transliteration']:
                score += 1
        return render_template('results.html', score=score, total=5, quiz_type="Multiple Choice")

    # Prepare questions and options
    questions = random.sample(all_phrases, 5)
    options = []
    for question in questions:
        wrong_answers = [p['transliteration'] for p in all_phrases if p['id'] != question['id']]
        options.append(random.sample(wrong_answers, 3) + [question['transliteration']])
        random.shuffle(options[-1])

    # Pre-zip questions and options before sending to the template
    zipped_data = zip(questions, options)
    return render_template('quiz_mc.html', zipped_data=zipped_data)

# Fill-in-the-Blank Quiz
@app.route('/quiz-fill', methods=['GET', 'POST'])
def quiz_fill():
    db = get_db()
    all_phrases = db.execute('SELECT * FROM phrases').fetchall()

    if request.method == 'POST':
        score = 0
        total = len(request.form)
        for phrase_id, user_answer in request.form.items():
            correct_answer = db.execute('SELECT english FROM phrases WHERE id = ?', (phrase_id,)).fetchone()
            if correct_answer and user_answer.strip().lower() == correct_answer['english'].strip().lower():
                score += 1
        return render_template('results.html', score=score, total=total, quiz_type="Fill-in-the-Blank")

    # Select 5 random phrases for the quiz
    questions = random.sample(all_phrases, 5)
    return render_template('quiz_fill.html', questions=questions)
# Initialize and seed the database
init_db()
seed_data()

if __name__ == '__main__':
    app.run(debug=True)