import os
from flask import Flask, render_template, url_for, redirect, flash
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length
from flask_bootstrap import Bootstrap


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SECRET_KEY'] = 'very_secret_string'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login = LoginManager(app)
login.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins='*')
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256))

    def __repr__(self):
        return '<User %r>' % self.username


class LoginForm(FlaskForm):
    username = StringField('Name', validators=[Length(min=3, max=12)])
    submit = SubmitField('Login')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@login_required
def index():
    user = current_user
    all_users = User.query.all()
    return render_template('index.html', user=user, all_users=all_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid name')
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@socketio.on('message')
def handleMessage(data):
    print(f"Message: {data}")
    send(data, broadcast=True)


@app.shell_context_processor
def make_shell():
    return {'app': app, 'db': db, 'User': User}


if __name__ == "__main__":
    socketio.run(app)