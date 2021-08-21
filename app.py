from Classes import *

db.create_all()

if User.query.count()==0:
    db.session.add(
        User(name='admin',passw=generate_password_hash('admin'),role='admin')
        )
    for i in 'Society','Economics','Sports':
        db.session.add(Theme(title=i))
    db.session.commit()

@app.route('/')
def main():
    return render_template('Lenta.html',cur=current_user,n=News.query.paginate(1,5,False),mx=News.query.count()%5,
                           themes=Theme.query.all())

@app.route('/p=<int:p>')
def page(p=None):
    if not p:
        return redirect('/')
    return render_template('News.html',cur=current_user,n=News.query.paginate(p,5,False),mx=News.query.count()%5,
                           themes=Theme.query.all())

@app.route('/news/<int:id_>')
def news(id_=None):
    if id_:
        coms=db.session.query(Comment,User,News).filter(Comment.user_id==User.id,Comment.n_id==News.id)
        return render_template('News.html',cur=current_user,n=News.query.get(id_),themes=Theme.query.all(),
                               coms=coms)
    return redirect('/')

@app.route('/<string:theme>')
@app.route('/<string:theme>/p=<int:p>')
def theme(theme=None,p=None):
    if not theme:
        return redirect('/')
    if not p:
        p=1
    data=News.query.filter_by(theme_id=Theme.query.filter_by(title=theme.capitalize()).first().id)
    return render_template('Lenta.html',cur=current_user,n=data.paginate(p,5,False),themes=Theme.query.all(),mx=data.count()%5)

@app.route('/add',methods=['POST'])
def add():
    image=request.files['image']
    n=News.query.count()+1
    image.save(
        os.path.join(fold,f'{n}.jpg')
        )
    new=News(title=request.form['title'],content=request.form['text'],
             theme_id=request.form['colls'])
    db.session.add(new)
    db.session.commit()
    return redirect(url_for('news',id_=News.query.count()))

@app.route('/<int:n_id>/save',methods=['POST'])
def save(n_id):
    News.query.get(n_id).content=request.form['text']
    db.session.commit()
    return redirect(url_for('news',id_=n_id))

@login_required
@app.route('/<n_id>/comment',methods=['POST'])
def comment(n_id):
    c=Comment(user_id=current_user.id,content=request.form['comment'],n_id=n_id)
    db.session.add(c)
    db.session.commit()
    return redirect(url_for('news',id_=n_id))

@app.route('/login',methods=['POST'])
def login():
    if request.method=='POST':
        name=request.form['name']
        passw=request.form['password']
        users=User.query.filter_by(name=name).all()
        if users:
            check=[check_password_hash(i.passw,passw) for i in users]
            if any(check):
                login_user(users[check.index(True)])
                return redirect('/')
            flash('Error')
    return redirect('/')

login_manager=LoginManager(app)
login_manager.login_view = '/login'
@login_manager.user_loader #загрузка пользователя
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/sign',methods=['POST','GET'])
def sign():
    if request.method=='POST':
        name=request.form['name']
        passw=request.form['password']
        users=User.query.filter_by(name=name).all()
        if users:
            check=[check_password_hash(i.passw,passw) for i in users]
            if any(check):
                flash('User already exists')
                return render_template('NewsSign.html')
        u=User(name=name,passw=generate_password_hash(passw))
        if current_user.is_authenticated:
            if current_user.role=='admin':
                u.role='admin'
        db.session.add(u)
        db.session.commit()
        load_user(User.query.count())
        return redirect('/')
    return render_template('NewsSign.html',cur=current_user,themes=Theme.query.all())

@login_required
@app.route('/logout',methods=['POST'])
def logout():
    logout_user()
    return redirect(request.referrer)

if __name__=='__main__':
    app.run()
