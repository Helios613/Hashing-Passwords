from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import bcrypt

# import cryptography
# from cryptography.fernet import Fernet
# file = open('key.key', 'rb') # rb = read bytes
# key  = file.read()
# file.close()
# print (key)
# fernet=Fernet(key)

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/blogdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name', None)
        userpass = request.form.get('pwd', None)
        hashed = bcrypt.hashpw(userpass.encode('utf-8'), bcrypt.gensalt())
        if not username or not userpass:
            flash('Username or password not provided')
            return render_template('sign-up.html')
    
        user = Users(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        return render_template('sign-in.html')
    return render_template('sign-up.html')


@app.route("/signin", methods=['GET', 'POST'])
def sigin():
    if 'user' in session:
        user = Users.query.filter_by(username=session['user']).first()
        return render_template('profile.html', user=user)
    if request.method=='POST':
        username = request.form.get('name')
        userpass = request.form.get('pwd')
        user = Users.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(userpass.encode('utf-8'), user.password.encode('utf-8')):
            session['user']=username
            return render_template('profile.html', user=user)

    return render_template('sign-in.html')

@app.route('/update/<string:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=="POST":
        username = request.form.get('name')
        userpass = request.form.get('pwd')
        hashed = bcrypt.hashpw(userpass.encode('utf-8'), bcrypt.gensalt()) 
        user = Users.query.filter_by(sno=sno).first()
        user.username = username
        user.password = hashed
        db.session.commit()   
        return redirect('/update/'+sno)

    user = Users.query.filter_by(sno=sno).first()
    return render_template('update.html', user=user)

@app.route('/signout')
def logout():
    session.pop('user')
    return redirect('/')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


app.run(debug=True)