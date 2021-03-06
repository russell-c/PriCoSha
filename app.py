from flask import render_template, Flask, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import sys

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
    
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (user))
    name = cursor.fetchone()

    query = "SELECT item_id, email_post, post_time, file_path, item_name FROM Content_Item WHERE is_pub = TRUE AND (DATEDIFF(CURDATE(), post_time)) <= 1"
    cursor.execute(query)
    content_items = cursor.fetchall()
    query2 = "SELECT share.item_id, email_post, post_time, file_path, item_name FROM person JOIN belong ON person.email = belong.member_email \
    JOIN share ON belong.owner_email = share.owner_email AND belong.fg_name = share.fg_name JOIN content_item ON share.item_id = content_item.item_id \
    WHERE member_email = %s"
    cursor.execute(query2, (user))
    shared_content_items = cursor.fetchall() 
    cursor.close()
    return render_template('home.html', name=name, contents=content_items, sharedContents=shared_content_items)

@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

@app.route('/manageTags')
def manageTags():
    user = session['email']
    cursor = conn.cursor()

    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (user))
    name = cursor.fetchone()
    
    query = "SELECT tagger_email, email_post, item_id, item_name FROM tag NATURAL JOIN content_item WHERE tagged_email = %s AND status = FALSE"
    cursor.execute(query, (user))
    requests = cursor.fetchall()
    cursor.close()
    return render_template('manageTags.html', user=name, requests=requests)

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
    cursor = conn.cursor()
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    username = cursor.fetchone() 

    user = session['email']
    item_id = int(request.form['id'])

    t_query = "SELECT f_name, l_name FROM (tag NATURAL JOIN content_item) JOIN person ON (tagged_email = person.email) WHERE item_id = %s AND status = TRUE"
    cursor.execute(t_query, (item_id))
    tags = cursor.fetchall()

    r_query = "SELECT * FROM rate WHERE item_id = %s"
    cursor.execute(r_query, (item_id))
    rates = cursor.fetchall()

    c_query = "SELECT * FROM comment WHERE item_id = %s"
    cursor.execute(c_query, (item_id))
    comments = cursor.fetchall()

    cursor.close()
    return render_template('ratingsAndTags.html', user=user, item=item_id, tags=tags, rates=rates, comments=comments, username=username)

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    user = session['email']
    item_id = int(request.form['id'])
    text = request.form['body']

    cursor = conn.cursor()
    query = "INSERT INTO comment (email, item_id, comment_time, comment) VALUES (%s, %s, CURRENT_TIMESTAMP, %s);"
    cursor.execute(query, (user, item_id, text))
    conn.commit()
    cursor.close()
    
    return redirect(url_for('home'))
    

@app.route('/tagUser', methods=['GET', 'POST'])
def tagUser():
    cursor = conn.cursor()
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    username = cursor.fetchone() 
    cursor.close()

    user = session['email']
    item_id = int(request.form['id'])
    
    return render_template('tagUser.html', user=user, item=item_id, username=username)

@app.route('/tag', methods=['GET', 'POST'])
def tag():
    cursor = conn.cursor()
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    username = cursor.fetchone() 

    user = session['email']
    email = request.form['email']
    item_id = int(request.form['id'])
    

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
            return render_template('tagUser.html', error=error, user=user, item=item_id, username=username)

@app.route('/post', methods=['GET', 'POST'])
def post():
    cursor = conn.cursor()

    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone() 
    return render_template('post_content.html', user=user)

@app.route('/post_item', methods=['POST'])
def post_item():
    cursor = conn.cursor()

    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone() 

    email = session['email']
    item_name = request.form['item_name']

    share = False
    if 'is_pub' in request.form:
        is_pub = request.form['is_pub']
    else:
        is_pub = "0"
        share = True
    
    file_path = request.form['file_path']

    if file_path:
        query = "INSERT INTO content_item (file_path, item_name, is_pub, email_post) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (file_path, item_name, is_pub, email))
    else:
        query = "INSERT INTO content_item (item_name, is_pub, email_post) VALUES (%s, %s, %s)"
        cursor.execute(query, (item_name, is_pub, email))
    
    conn.commit()
    id = cursor.lastrowid
    cursor.close()

    if share:
        return render_template('share.html', id=id, user=user)
    else:
        return redirect(url_for('post'))

@app.route('/share', methods=["GET"])
def share():
    return render_template('share.html')

@app.route('/share_item', methods=["POST"])
def share_item():
    fg = request.form['friendgroup']
    item_id = request.form['item_id']
    email = session['email']

    cursor = conn.cursor()
    query = "INSERT INTO share VALUES(%s, %s, %s)"
    cursor.execute(query, (item_id, email, fg))
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))

@app.route('/add', methods=['GET'])
def add():
    cursor = conn.cursor()
    email = session['email']
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone()

    query = 'SELECT fg_name FROM friend_group WHERE email = %s'
    cursor.execute(query, (email))

    fgs = cursor.fetchall()
    cursor.close()

    return render_template('add.html', friend_groups=fgs, user=user)


@app.route('/add/<friend_group>', methods=['GET', 'POST'])
def add_friend(friend_group):
    cursor = conn.cursor()
    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone() 
    cursor.close()

    success = False
    persons = None

    return render_template('add_friend.html', user=user, friend_group=friend_group, persons=persons, success=success)

@app.route('/add/<friend_group>/find', methods=['POST'])
def find_friends(friend_group):
    cursor = conn.cursor()

    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone() 

    fname = request.form['fname']
    lname = request.form['lname']

    query = "SELECT f_name, l_name, email FROM person WHERE f_name = %s AND l_name = %s"
    cursor.execute(query, (fname, lname))
    persons = cursor.fetchall()
    cursor.close()

    if persons: 
        success = True
        return render_template('add_friend.html', user=user, friend_group=friend_group, persons=persons, success=success)
    else:
        return redirect(url_for('home'))

@app.route('/add/<friend_group>/<friend_email>', methods=['GET', 'POST'])
def add_friend_to_group(friend_group, friend_email):
    cursor = conn.cursor()
    curr_user = session['email'].lower()
    query = 'INSERT INTO belong VALUES(%s, %s, %s)'
    cursor.execute(query, (curr_user, friend_group, friend_email))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/remove', methods=['GET'])
def remove():
    cursor = conn.cursor()

    query = 'SELECT f_name, l_name, email FROM person WHERE email in (SELECT DISTINCT(member_email) FROM belong WHERE owner_email = %s) \
        AND email != %s'
    cursor.execute(query, (session['email'], session['email']))
    friends = cursor.fetchall()

    query = "SELECT f_name, l_name FROM person WHERE email = %s"
    cursor.execute(query, (session['email']))
    user = cursor.fetchone() 
    cursor.close()

    return render_template('remove.html', user=user, friends=friends)

@app.route('/remove/<friend_email>', methods=['GET', 'POST'])
def remove_friend(friend_email):
    cursor = conn.cursor()
    curr_user = session['email']
    
    query = "DELETE FROM belong WHERE owner_email = %s AND member_email = %s"
    cursor.execute(query, (curr_user, friend_email))

    query = "DELETE FROM tag WHERE tagger_email = %s AND tagged_email = %s"
    cursor.execute(query, (curr_user, friend_email))
    conn.commit()

    cursor.close()

    return redirect(url_for('remove'))


app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)