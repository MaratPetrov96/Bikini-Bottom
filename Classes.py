from flask import Flask,render_template,abort,request,redirect,url_for
from flask_login import UserMixin,logout_user,login_user,current_user,login_required,LoginManager
from werkzeug.security import check_password_hash,generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin,BaseView,expose,AdminIndexView
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField
import os

fold='news'
app=Flask(__name__,static_folder=fold)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SECRET_KEY']='key'

db=SQLAlchemy(app)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    name=db.Column(db.String(32),nullable=False)
    passw=db.Column(db.String(128),nullable=False)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    role=db.Column(db.String(8),nullable=False,default='user')
    def __repr__(self):
        return self.name

class News(db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    title=db.Column(db.String(64),nullable=False)
    content=db.Column(db.Text,nullable=False)
    theme_id=db.Column(db.Integer,db.ForeignKey('theme.id'),nullable=False)
    comments=db.relationship('Comment',backref='newss',lazy='dynamic')
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    n_id=db.Column(db.Integer,db.ForeignKey('news.id'),nullable=False)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

class Theme(db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    title=db.Column(db.String(32),nullable=False)

class Select(FlaskForm):
    colls=SelectField(u'News theme', choices=[(f'{c.id}', c.title) for c in Theme.query.all()])

class Panel(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('Lenta.html',cur=current_user,n=News.query.paginate(1,5,False),mx=News.query.count()%5,
                           themes=Theme.query.all())
    def is_accessible(self):
        return current_user.role=='admin'
    def inaccessible_callback(self):
        return redirect('login')

class NewRecord(BaseView):
    @expose('/')
    def record(self):
        return self.render('NewsRecord.html',cur=current_user,themes=Theme.query.all(),select=Select())
    def is_accessible(self):
        return current_user.role=='admin'
    def inaccessible_callback(self):
        return redirect('login')
admin=Admin(app,index_view=Panel())
admin.add_view(NewRecord(name='new_record',endpoint='record'))
