from flask import render_template, Flask, request, session, url_for, redirect
import pymysql.cursors
import hashlib

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       port=8889,
                       user='root',
                       password='root',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor
                    )

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    email = request.form['email']
    password = request.form['password']
    hashedPassword = hashlib.sha256(password.encode()).hexdigest()
    print(hashedPassword)

    cursor = conn.cursor()

    query = 'SELECT * FROM person WHERE email = %s AND password = %s'
    cursor.execute(query, (email, hashedPassword))
    data = cursor.fetchone()

    cursor.close()
    error = None

    if(data):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        error = 'Invalid email address or password'
        return render_template('login.html', error=error)

@app.route('/home')
def home():
    user = session['email']
    cursor = conn.cursor()
    
    query = "SELECT item_id, post_time, file_path, item_name FROM Content_Item WHERE is_pub = TRUE AND (DATEDIFF(CURDATE(), post_time)) <= 1"
    cursor.execute(query)
    content_items = cursor.fetchall() 
    cursor.close()
    print(content_items)
    return render_template('home.html', user=user, contents=content_items)

app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)