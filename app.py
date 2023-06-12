#modules used
from flask import Flask,render_template,url_for,redirect #url management
from flask_sqlalchemy import SQLAlchemy #import database
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user #manage user sessions
from flask_wtf import FlaskForm #create form
from wtforms import StringField, PasswordField, SubmitField #create input fields
from wtforms.validators import InputRequired, Length, ValidationError #validate user inputs
from flask_bcrypt import Bcrypt #for password hashing

#create app instance
app = Flask(__name__)
bcrypt = Bcrypt(app)

#connect app file to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/ICT/Documents/projects/flask-projects/database.db'
#create secret key
app.config['SECRET_KEY'] = 'thisisasecretkey'
#create database instance
db = SQLAlchemy(app)

"""Create database table with three columns"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

"""Create tables in database db"""
@app.route('/create')
def create():
    db.create_all()
    return 'All tables created'

"""Login manager to ensure session does not end"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""Create a registration form using FlaskForm"""
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')
    #Validate username to ensure does not exist in database
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        #if user present return error
        if existing_user_username:
              raise ValidationError('That username already exists. Please choose a different one.')
"""Create a login form using FlaskForm"""
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#homepage
@app.route("/")
def home():
    return render_template('home.html')

#login page
@app.route("/login",methods = ["GET","POST"])
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html',form = form)

#register page
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template('register.html',form = form)

#dashboard page
@app.route("/dashboard",methods = ["GET","POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

#logout page
@app.route("/logout",methods = ["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#create condition for app to only run in main file
if __name__ == '__main__':
    #run app if condition met
    app.run(debug=True) 