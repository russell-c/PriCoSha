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

@app.route('/home', methods=['GET', 'POST'])
def home():
    user = session['email']
    cursor = conn.cursor()
    
    query = "SELECT item_id, email_post, post_time, file_path, item_name FROM Content_Item WHERE is_pub = TRUE AND (DATEDIFF(CURDATE(), post_time)) <= 1"
    cursor.execute(query)
    content_items = cursor.fetchall()
    query2 = "SELECT share.item_id, email_post, post_time, file_path, item_name FROM person JOIN belong ON person.email = belong.member_email \
    JOIN share ON belong.owner_email = share.owner_email AND belong.fg_name = share.fg_name JOIN content_item ON share.item_id = content_item.item_id \
    WHERE member_email = %s"
    cursor.execute(query2, (user))
    shared_content_items = cursor.fetchall() 
    cursor.close()
    return render_template('home.html', user=user, contents=content_items, sharedContents=shared_content_items)

@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

@app.route('/manageTags')
def manageTags():
    user = session['email']
    cursor = conn.cursor()
    
    query = "SELECT tagger_email, email_post, item_id, item_name FROM tag NATURAL JOIN content_item WHERE tagged_email = %s AND status = FALSE"
    cursor.execute(query, (user))
    requests = cursor.fetchall()
    cursor.close()
    return render_template('manageTags.html', user=user, requests=requests)

@app.route('/approve', methods=['GET', 'POST'])
def approve():
    user = session['email']
    tagger_email = request.form['tagger']
    tagged_email = request.form['tagged']
    item_id = int(request.form['id'])
    decision = request.form['yes']
    cursor = conn.cursor()

    if decision == 'YES':
        query = "UPDATE tag SET status = TRUE WHERE tagged_email = %s AND tagger_email = %s AND item_id = %s"
    elif decision == 'NO':
        query = "DELETE FROM tag WHERE tagged_email = %s AND tagger_email = %s AND item_id = %s"

    cursor.execute(query, (tagged_email, tagger_email, item_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('manageTags'))

@app.route('/ratingsAndTags', methods=['GET', 'POST'])
def viewRatingAndTags():
    user = session['email']
    cursor = conn.cursor()
    item_id = int(request.form['id'])

    t_query = "SELECT f_name, l_name FROM (tag NATURAL JOIN content_item) JOIN person ON (tagged_email = person.email) WHERE item_id = %s AND status = TRUE"
    cursor.execute(t_query, (item_id))
    tags = cursor.fetchall()

    r_query = "SELECT * FROM rate WHERE item_id = %s"
    cursor.execute(r_query, (item_id))
    rates = cursor.fetchall()

    cursor.close()
    return render_template('ratingsAndTags.html', item=item_id, tags=tags, rates=rates)

@app.route('/tagUser', methods=['GET', 'POST'])
def tagUser():
    user = session['email']
    item_id = int(request.form['id'])
    return render_template('tagUser.html', user=user, item=item_id)

@app.route('/tag', methods=['GET', 'POST'])
def tag():
    user = session['email']
    email = request.form['email']
    item_id = int(request.form['id'])
    cursor = conn.cursor()

    if user == email:
        query = "INSERT INTO tag (tagged_email, tagger_email, item_id, tag_time, status) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, '1');"
        cursor.execute(query, (user, user, item_id))
        conn.commit()
        cursor.close()
        return redirect(url_for('home'))
    else:
        check_query = 'SELECT share.item_id, email_post, post_time, file_path, item_name FROM person JOIN belong ON person.email = belong.member_email \
        JOIN share ON belong.owner_email = share.owner_email AND belong.fg_name = share.fg_name JOIN content_item ON share.item_id = content_item.item_id \
        WHERE member_email = %s'
        cursor.execute(check_query, (email))
        data = cursor.fetchone()

        error = None

        if(data):
            query = "INSERT INTO tag (tagged_email, tagger_email, item_id, tag_time, status) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, '0');"
            cursor.execute(query, (email, user, item_id))
            conn.commit()
            cursor.close()
            return redirect(url_for('home'))
        else:
            error = 'This item is not visible to that user'
            cursor.close()
            return render_template('tagUser.html', error=error)


app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)