from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7706",
    database="dbms"
)

mycursor = mydb.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        mycursor.execute("SELECT password FROM user_counter WHERE user_name = %s", (user_name,))
        result = mycursor.fetchone()
        if result and result[0] == password:
            session['username'] = user_name
            return redirect(url_for('dashboard'))
        else:
            a="Login failed.\n Check your username and password.\n Or maybe you have not created an account please go to sign page"
            return a
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        dob = request.form['dob']
        mycursor.execute("SELECT user_name FROM user_counter WHERE user_name = %s", (user_name,))
        result = mycursor.fetchone()
        if result:
            return "User already exists. Please log in."
        else:
            mycursor.execute("INSERT INTO user_counter (user_name, password, dob, age) VALUES (%s, %s, %s, %s)", (user_name, password, dob, 2000))
            mydb.commit()
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/create_channel', methods=['POST'])
def create_channel():
    user_id = session['username']
    channel_name = request.form['channel_name']
    channel_password = request.form['channel_password']
    mycursor.execute("SELECT channel_name FROM channel_counter WHERE channel_name = %s", (channel_name,))
    result = mycursor.fetchone()
    if result:
        return "Channel already exists. Please choose a different name."
    else:
        description = request.form['description']
        channel_id = user_id + channel_name
        mycursor.execute("INSERT INTO channel_counter (channel_id, user_id, channel_name, channel_description, channel_password) VALUES (%s, %s, %s, %s, %s)", (channel_id, user_id, channel_name, description, channel_password))
        mydb.commit()
        mycursor.execute(f"CREATE TABLE {channel_name} (video_id VARCHAR(255), video_name VARCHAR(255), video_data LONGBLOB, video_description VARCHAR(255), image_id VARCHAR(255), image_name VARCHAR(255), image_data LONGBLOB, image_description VARCHAR(255))")
        mydb.commit()
        return "Channel created successfully."

@app.route('/upload_content', methods=['POST'])
def upload_content():
    channel_id = request.form['channel_id']
    channel_password = request.form['channel_password']
    mycursor.execute("SELECT channel_name FROM channel_counter WHERE channel_id = %s AND channel_password = %s", (channel_id, channel_password))
    result = mycursor.fetchone()
    if not result:
        return "Invalid channel ID or password."
    
    channel_name = result[0]
    content_type = request.form['content_type']
    content_name = request.form['content_name']
    content_data = request.form['content_data']
    content_description = request.form['content_description']
    
    if content_type == 'video':
        video_id = content_name + channel_id
        command = f"INSERT INTO {channel_name} (video_id, video_name, video_data, video_description) VALUES (%s, %s, %s, %s)"
        mycursor.execute(command, (video_id, content_name, content_data, content_description))
    elif content_type == 'image':
        image_id = content_name + channel_id
        command = f"INSERT INTO {channel_name} (image_id, image_name, image_data, image_description) VALUES (%s, %s, %s, %s)"
        mycursor.execute(command, (image_id, content_name, content_data, content_description))
    mydb.commit()
    return "Content uploaded successfully."

@app.route('/search', methods=['POST'])
def search():
    search_image = request.form['search_image']
    search_video = request.form['search_video']
    v = "%"
    results = []

    mycursor.execute("SELECT channel_name FROM channel_counter")
    channels = mycursor.fetchall()
    for channel in channels:
        channel_name = channel[0]

        command = f"SELECT video_id, video_name, video_data, video_description FROM {channel_name} WHERE video_name LIKE %s"
        mycursor.execute(command, (v + search_video + v,))
        results.extend(mycursor.fetchall())

        command = f"SELECT image_id, image_name, image_data, image_description FROM {channel_name} WHERE image_name LIKE %s"
        mycursor.execute(command, (v + search_image + v,))
        results.extend(mycursor.fetchall())

    return render_template('search_result.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
