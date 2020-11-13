from flask import Flask, jsonify, request, render_template, redirect
import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for,flash, redirect, request,abort
from flask_login import login_user,current_user,logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
from flask_login import UserMixin
from bot import chatbot_response

# App Configurations section
app = Flask(__name__)

app.config['SECRET_KEY'] = '14b16d9389500acd8364f0b2996e222f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/edyycoders/Desktop/1.class/1.eddyFinal/OriginalV2/site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# from quabot import routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# End of app Configurations section

# Application Model Section

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60),nullable=False)

    
    def get_reset_token(self, expires_sec=1800):
        s =  Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id: self.id'}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s =  Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}',{self.email}','{self.image_file}')"

# End of Model section

# ****************************Forms Declarations*********************
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username exists,Please pick another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email exists,Please pick another one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username exists,Please pick another one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email exists,Please pick another one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email,You must register First')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Request Password Reset')

# ****************************End of Forms Declarations*********************

#======================Routes Section ==============================
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unssuccessful.Please Check your Username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created you can  now Login','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# @app.route("/chat")
# @login_required
# def chat():
#     return render_template("chat.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

#Account route
@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.username.data
        db.session.commit()
        flash('Your Account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data == current_user.username
        form.email.data == current_user.email
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account', 
                            image_file=image_file, form=form)

##Functinality of saving a picture.
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn


                    
#Password Reset Route.
@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password',form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your Password has been updated!','success')
        return redirect(url_for('login'))

    return render_template('reset_token.html',title='Reset Password', form=ResetPasswordForm)

def send_reset_email(user):
    token =  user.get_reset_token()
    msg = Message('Password Reset Request',
                 sender='noreply@demo.com',
                 recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token,_external=True)}

If you did not make this request,Then simply ignore this email and no changes will be made
'''
    mail.send(msg)
# ***********************End Of Routes Configurations**********************


@app.route('/chat-api', methods=['POST'])
def get_bot_response():
    print(request.json)
    msg = request.json.get('msg')
    print(f'QUESTION: {msg}')
    answer = chatbot_response(msg)
    print(f'ANSWER: {answer}')

    return jsonify({
        'msg':msg,
        'answer': answer
    })


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
# def get_chatbot_response():
    return render_template('chat.html')


@app.route("/get", methods=['GET','POST'])
#function for the bot response
def get(): 
        msg = request.args.get('msg')
        answer = chatbot_response(msg)
        return  answer                                                                                              

#======================Routes Section ==============================

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
