from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
from datetime import datetime
import traceback
 
app = Flask(__name__)

# connection to the database
def create_connection():
    conn = sqlite3.connect('data.db')
    return conn

# Start on quiz page
@app.route('/')
def index():
    return render_template('quiz.html')


# gets next question
@app.route('/next_question')
def next_question():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_text, number_answer FROM Questions ORDER BY RANDOM() LIMIT 1")
    question = cursor.fetchone()
    conn.close()

    if question:
        question_text = question[0]
        number_answer = question[1].replace('\\boxed{', '').replace('}', '')
        count = 0
        while '$' in question_text:
            if count % 2 == 0:
                question_text = question_text.replace('$', '\\(', 1)
            else:
                question_text = question_text.replace('$', '\\)', 1)
            count += 1
        return jsonify({'question': question_text, 'answer': number_answer})
    else:
        return jsonify({'question': None, 'answer': None})
        
    


# stores the user's answer
@app.route('/store_answer', methods=['POST'])
def store_answer():
    user_answer = request.json['userAnswer']
    correct_answer = request.json['correctAnswer']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO UserAnswers (user_id, question_id, user_answer, correct_answer, is_correct) VALUES (?, ?, ?, ?, ?)', (1, 1, user_answer, correct_answer, user_answer.lower() == correct_answer.lower()))
    conn.commit()
    conn.close()
        
# sign up
@app.route('/add', methods=['POST'])
def add_data():
    user_id = random.randint(0,5000)
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    password = request.form['pass']
    
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (id, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)',  (user_id, fname, lname, email, password))

    conn.commit()
    conn.close()
    

    
    return redirect(url_for('quiz'))

# log in
@app.route('/get', methods=['POST'])
def login():
    email = request.form['loginEmail']
    password = request.form['loginPass']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()

    if user:
        conn.close()
        return redirect(url_for('quiz'))
    else:
        conn.close()  
        return "Invalid email or password"

if __name__ == '__main__':
    app.run(debug=True)


        
       