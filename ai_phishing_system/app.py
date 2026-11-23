import os, sqlite3, pickle, re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'data', 'phishing.db')
MODEL_PATH = os.path.join(BASE, 'model', 'phishing_model.pkl')
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key')


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = db()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject TEXT,
        email_text TEXT NOT NULL,
        prediction TEXT NOT NULL,
        confidence REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    admin = conn.execute('SELECT id FROM users WHERE username=?', ('admin',)).fetchone()
    if not admin:
        conn.execute('INSERT INTO users(username,password_hash,role) VALUES(?,?,?)',
                     ('admin', generate_password_hash('admin123'), 'admin'))
    conn.commit(); conn.close()


def train_model():
    if os.path.exists(MODEL_PATH):
        return
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    samples = [
      ('urgent verify your account password immediately click this link', 1),
      ('your bank account is suspended confirm your identity now', 1),
      ('congratulations you won a prize send your card details', 1),
      ('security alert unusual login verify your account at the link below', 1),
      ('final notice update payment information to avoid cancellation', 1),
      ('claim your reward by entering your password and otp', 1),
      ('dear customer click here to unlock your account immediately', 1),
      ('invoice attached please review the monthly invoice for our project', 0),
      ('team meeting is scheduled for tomorrow at 10 am', 0),
      ('your order has shipped and will arrive on friday', 0),
      ('please find the report attached for your review', 0),
      ('thanks for your email we will discuss this in the meeting', 0),
      ('your subscription receipt is available in your account', 0),
      ('the project deadline has been moved to next monday', 0),
      ('welcome to the company here are your onboarding documents', 0),
    ]
    X=[x for x,y in samples]; y=[y for x,y in samples]
    pipe=Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, max_features=5000)),
                   ('clf',LogisticRegression(max_iter=1000))])
    pipe.fit(X,y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH,'wb') as f: pickle.dump(pipe,f)


def load_model():
    with open(MODEL_PATH,'rb') as f: return pickle.load(f)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Administrator access required.', 'danger'); return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


def analyze(text):
    text = re.sub(r'\s+', ' ', text).strip()
    model=load_model(); probs=model.predict_proba([text])[0]
    classes=list(model.classes_); phishing_prob=float(probs[classes.index(1)])
    prediction='Phishing' if phishing_prob >= 0.5 else 'Legitimate'
    confidence=phishing_prob if prediction=='Phishing' else 1-phishing_prob
    return prediction, round(confidence*100,2)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username'].strip(); password=request.form['password']
        if len(username)<3 or len(password)<6: flash('Username must be 3+ chars and password 6+ chars.','danger'); return render_template('register.html')
        conn=db()
        try:
            conn.execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(username,generate_password_hash(password))); conn.commit()
            flash('Registration successful. Please log in.','success'); return redirect(url_for('login'))
        except sqlite3.IntegrityError: flash('Username already exists.','danger')
        finally: conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']; password=request.form['password']; conn=db(); user=conn.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone(); conn.close()
        if user and check_password_hash(user['password_hash'],password):
            session.update(user_id=user['id'], username=user['username'], role=user['role']); return redirect(url_for('dashboard'))
        flash('Invalid username or password.','danger')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn=db(); rows=conn.execute('SELECT * FROM detections WHERE user_id=? ORDER BY id DESC LIMIT 10',(session['user_id'],)).fetchall(); conn.close()
    return render_template('dashboard.html', rows=rows)

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_email():
    subject=request.form.get('subject',''); text=request.form.get('email_text','').strip()
    if not text: flash('Please enter email content.','danger'); return redirect(url_for('dashboard'))
    prediction, confidence=analyze(subject+' '+text)
    conn=db(); conn.execute('INSERT INTO detections(user_id,subject,email_text,prediction,confidence) VALUES(?,?,?,?,?)',(session['user_id'],subject,text,prediction,confidence)); conn.commit(); conn.close()
    return render_template('result.html', subject=subject, text=text, prediction=prediction, confidence=confidence)

@app.route('/history')
@login_required
def history():
    conn=db(); rows=conn.execute('SELECT * FROM detections WHERE user_id=? ORDER BY id DESC',(session['user_id'],)).fetchall(); conn.close(); return render_template('history.html',rows=rows)

@app.route('/admin')
@login_required
@admin_required
def admin():
    conn=db(); users=conn.execute('SELECT id,username,role,created_at FROM users ORDER BY id DESC').fetchall(); detections=conn.execute('SELECT d.*,u.username FROM detections d JOIN users u ON u.id=d.user_id ORDER BY d.id DESC LIMIT 50').fetchall(); conn.close(); return render_template('admin.html',users=users,detections=detections)

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    data=request.get_json(silent=True) or {}; text=(data.get('subject','')+' '+data.get('email_text','')).strip()
    if not text: return jsonify({'error':'email_text is required'}),400
    prediction, confidence=analyze(text); return jsonify({'prediction':prediction,'confidence':confidence})

if __name__=='__main__':
    init_db(); train_model(); app.run(debug=True)
