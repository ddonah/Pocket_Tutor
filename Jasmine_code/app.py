from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
import traceback

app = Flask(__name__, static_folder='static')
logged_in_user_id = None
question_count = 0
user_answer_id = str(random.randint(0, 1000000))

# connection 
def create_connection():
    conn = sqlite3.connect('data.db')
    return conn

#begins on login_quiz.html
@app.route('/')
def index():
    return render_template('login_quiz.html')
    
# register_quiz.html
@app.route('/register_quiz.html')
def register():
    return render_template('register_quiz.html')
  
#login_quiz.html  
@app.route('/login_quiz.html')
def login():
    return render_template('login_quiz.html')  

# show_quiz.html
@app.route('/quiz')
def quiz():
    return render_template('show_quiz.html')

# recap_quiz.html
@app.route('/recap')
def recap():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Questions.question_text, UserAnswers.user_answer, UserAnswers.correct_answer AS user_correct_answer, Questions.correct_answer AS question_correct_answer FROM UserAnswers JOIN Questions ON UserAnswers.question_id = Questions.question_id WHERE UserAnswers.user_answer_id = ? AND UserAnswers.is_correct = 0", (user_answer_id,))
        wrong_answers = cursor.fetchall()        
        conn.close()
        return render_template('recap_quiz.html', correct_answers_count=correct_answers_count, wrong_answers=wrong_answers)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# gets the next questions and stops the quiz at 10 questions
@app.route('/next_question')
def next_question():
    global question_id
    global question_count
    global user_answer_id
    if question_count >= 10:
        return jsonify({'quiz_finished': True})  
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_text, answer, question_id FROM Questions ORDER BY RANDOM() LIMIT 1")
    question = cursor.fetchone()
    conn.close()
    if question:
        question_text = question[0]
        number_answer = question[1]
        question_id = question[2]
        count = 0
        while '$' in question_text:
            if count % 2 == 0:
                question_text = question_text.replace('$', '\\(', 1)
            else:
                question_text = question_text.replace('$', '\\)', 1)
            count += 1
        question_count += 1
        return jsonify({'question': question_text, 'answer': number_answer, 'quiz_finished': False, 'question_count': question_count, 'user_answer_id': user_answer_id})
    else:
        return jsonify({'quiz_finished': True})  
correct_answers_count = 0

# stores user's answer in db
@app.route('/store_answer', methods=['POST'])
def store_answer():
    global logged_in_user_id
    global question_id
    global correct_answers_count
    global user_answer_id
    
    try:
        user_answer = request.json['userAnswer']
        correct_answer = request.json['correctAnswer']
        is_correct = user_answer.lower() == correct_answer.lower()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO UserAnswers (user_answer_id, user_id, question_id, user_answer, correct_answer, is_correct) VALUES (?, ?, ?, ?, ?, ?)', (user_answer_id, logged_in_user_id, question_id, user_answer, correct_answer, is_correct))
        conn.commit()
        if is_correct:
            correct_answers_count += 1
        conn.close()
        return jsonify({'success': True, 'is_correct': is_correct})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# signup for users
@app.route('/signup', methods=['POST'])
def signup():
    global logged_in_user_id
    try:
        data = request.json
        fname = data['fname']
        lname = data['lname']
        email = data['email']
        password = data['pass']
        conn = create_connection()
        cursor = conn.cursor()
        user_id = random.randint(0, 5000)
        cursor.execute('INSERT INTO Users (id, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)', (user_id, fname, lname, email, password))
        logged_in_user_id = user_id
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# login for users
@app.route('/user_login', methods=['POST'])
def user_login():
    global logged_in_user_id
    try:
        data = request.json
        email = data['email']
        password = data['password']
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ?', (email, password))
        user_id = cursor.fetchone()
        if user_id:
            logged_in_user_id = user_id[0]
            conn.close()
            return jsonify({'success': True})
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
