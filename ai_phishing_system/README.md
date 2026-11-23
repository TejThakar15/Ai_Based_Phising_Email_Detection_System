# AI-Based Phishing Email Detection System

A working MCA minor-project prototype based on the uploaded project report. It uses Python + Flask, NLP with TF-IDF, Logistic Regression, authentication, detection history, and an administrator dashboard.

## Features
- User registration and login
- AI classification: Phishing / Legitimate
- TF-IDF NLP feature extraction + Logistic Regression classifier
- Confidence score
- Detection history
- Admin dashboard
- JSON API at `/api/analyze`
- SQLite for zero-configuration demo; database layer can be replaced with MySQL for deployment

## Run on Windows
1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run `py -m venv venv`
4. Run `venv\Scripts\activate`
5. Run `pip install -r requirements.txt`
6. Run `python app.py`
7. Open `http://127.0.0.1:5000`

## Demo accounts
- Admin username: `admin`
- Admin password: `admin123`

Change the admin password and Flask secret before real deployment.

## Important academic note
The included training set is intentionally small so the project runs immediately. For a serious evaluation, train the model on a larger labelled phishing/legitimate email dataset and report precision, recall, F1-score, confusion matrix, and test accuracy. Do not treat the prototype's prediction as a security guarantee.

## Report alignment
The uploaded report specifies HTML5/CSS3/JavaScript/Bootstrap, Python/Flask, Machine Learning/NLP, and MySQL. This prototype implements the same architecture, with SQLite as the default local database to make the demo immediately runnable. MySQL can be added as the production database layer.
