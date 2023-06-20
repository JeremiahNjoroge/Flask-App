#modules used
from flask import Flask,render_template,url_for,redirect,request#url management
from flask_sqlalchemy import SQLAlchemy #import database
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user #manage user sessions
from flask_wtf import FlaskForm #create form
from wtforms import StringField, PasswordField, SubmitField, SelectField #create input fields
from wtforms.validators import InputRequired, Length, ValidationError #validate user inputs
from flask_bcrypt import Bcrypt #for password hashing
from sqlalchemy import Enum
from datetime import datetime
from wtforms.fields import DateField
from flask import flash

#create app instance
app = Flask(__name__,static_url_path='/static')
bcrypt = Bcrypt(app)

#connect app file to database
#C:\Users\jere\Documents\Projects\Flask-App\database.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/jere/Documents/Projects/Flask-App/database.db'
#create secret key
app.config['SECRET_KEY'] = 'thisisasecretkey'
#create database instance
db = SQLAlchemy(app)

"""Create database table with three columns"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
"""Create table farmer"""
class Farmer(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    gender = db.Column(Enum('Male', 'Female', name='gender_enum'), nullable=False)
    dateofbirth = db.Column(db.Date, nullable=False)
    IDNo = db.Column(db.String(20), nullable=False, unique = True)

class Coffee(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False)


class Milk(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False)



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
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username","autocomplete":"off"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

"""Create farmer profile form"""
class FarmerProfileForm(FlaskForm):
    first_name = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Firstname", "autocomplete": "off"})
    surname = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Surname", "autocomplete": "off"})
    mobile = StringField(validators=[InputRequired(), Length(min=10, max=12)], render_kw={"placeholder": "Mobile", "autocomplete": "off"})
    gender = SelectField(validators=[InputRequired()], choices=[('Male', 'Male'), ('Female', 'Female')], render_kw={"placeholder": "Gender", "autocomplete": "off"})
    dateofbirth = DateField('Date of Birth', validators=[InputRequired()], format='%Y-%m-%d')    
    IDNo = StringField(validators=[InputRequired(), Length(min=5, max=12)], render_kw={"placeholder": "ID Number", "autocomplete": "off"})
    submit = SubmitField('Create Profile')
    def validate_user_id():
        existing_id_no = Farmer.query.filter_by(IDNo=IDNo.data).first()
        if existing_id_no:
            raise ValidationError('That ID number already exists. Please enter a different one.')
    def validate_dateofbirth(self, dateofbirth):
        try:
            datetime.strptime(str(dateofbirth.data), '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Invalid date format. Please use the format YYYY-MM-DD.')
    
    def convert_dateofbirth(self):
        return datetime.strptime(str(self.dateofbirth.data), '%Y-%m-%d').date()

class ProduceForm(FlaskForm):
    harvest_date = DateField('Harvest Date', validators=[InputRequired()], format='%Y-%m-%d')
    quantity = StringField('Quantity Harvested', validators=[InputRequired()])
    submit = SubmitField('Store Produce')

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
    profile = Farmer.query.filter_by(username=current_user.username).first()

    if profile:
        link_text = "Update Profile"
        link_url = url_for('updateprofile')
    else:
        link_text = "Create Profile"
        link_url = url_for('farmerprofile')


    return render_template('dashboard.html', link_text=link_text, link_url=link_url)

@app.route("/produce/<produce_type>", methods=["GET", "POST"])
@login_required
def produce(produce_type):
    return render_template('produce.html')

@app.route("/farmerprofile",methods=["GET","POST"])
@login_required
def farmerprofile():
    form = FarmerProfileForm()
    
    if form.validate_on_submit():
        # Create a new instance of the Farmer class and assign form data to its attributes
        new_farmer = Farmer(
            username=current_user.username,
            first_name=form.first_name.data,
            surname=form.surname.data,
            mobile=form.mobile.data,
            gender=form.gender.data,
            dateofbirth=form.convert_dateofbirth(),
            IDNo=form.IDNo.data
        )

        # Add the new farmer profile to the database session and commit the changes
        db.session.add(new_farmer)
        db.session.commit()
        flash("Profile successfully created", "success")
        return redirect(url_for('dashboard'))
    return render_template('farmerprofile.html',form = form)

@app.route('/viewprofile')
@login_required
def viewprofile():
    # Logic to retrieve the profile data for the current user
    profile = Farmer.query.filter_by(username=current_user.username).first()
    return render_template('viewprofile.html', profile=profile)

@app.route('/updateprofile', methods=["GET", "POST","DELETE","PUT"])
@login_required
def updateprofile():
    profile = Farmer.query.filter_by(username=current_user.username).first()
    form = FarmerProfileForm(obj=profile)
    
    if form.validate_on_submit():
        # Update the existing profile with the new form data
        profile.first_name = form.first_name.data
        profile.surname = form.surname.data
        profile.mobile = form.mobile.data
        profile.gender = form.gender.data
        profile.dateofbirth = form.convert_dateofbirth()
        profile.IDNo = form.IDNo.data

        db.session.commit()
        flash("Profile successfully updated", "success")
        return redirect(url_for('dashboard'))

    return render_template('updateprofile.html', form=form)
    
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