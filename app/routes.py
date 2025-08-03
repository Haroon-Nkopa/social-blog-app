from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, registrationForm, EditProfileForm, EmptyForm, PostForm, password_reset_request, Reset_Password
import sqlalchemy as sa
from app.models import User, Post
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.emails import send_password_reset_request_email
from flask_babel import _

@app.route("/", methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    postForm = PostForm()
    if postForm.validate_on_submit():
        post = Post( body=postForm.postText.data, author=current_user )
        db.session.add(post)
        db.session.commit()
        flash(_('your post is live.'))
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    posts= db.paginate(current_user.following_posts() , page=page, per_page=app.config['POST_PER_PAGE'], error_out=False)
    next_url = url_for('index', page= posts.next_num ) \
        if posts.has_next else None
    prev_url = url_for('index', page= posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='home page', posts= posts.items, form = postForm, prev_url= prev_url, next_url= next_url)

@app.route('/login', methods= ['GET', 'POST'])
def login():

    # we need to check if the user is locked in before rendering that file.
    #if the current_user is loged in then we redirect to index page. 
    #if not 
    if current_user.is_authenticated:

        return redirect(url_for('index'))
    _form = LoginForm()
    if _form.validate_on_submit():
        #get theuser from the databse that matches the name. 
        query = sa.select(User).where(User.username == _form.username.data)
        user = db.session.scalar(query)
        if user is None or not user.check_password(_form.password.data):
            flash(_("Invalide crediatials"))
            return redirect(url_for('login'))
        login_user(user, remember=_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = 'index'
        return redirect(url_for(next_page))
        
    return render_template('login.html', form= _form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    #need to make sure the user is not logged in. 
    if current_user.is_authenticated :
        return redirect(url_for('index'))
    #create a registerForm 
    form = registrationForm()
    if form.validate_on_submit():
        #create user
        newUser = User(username=form.username.data, email=form.email.data)
        newUser.set_password(form.password.data)
        db.session.add(newUser)
        db.session.commit()
        flash(_('successfully one of the greatness now. Welcome.'))
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/user/<username>')
@login_required
def user(username):
    #make a erquest to the database. 
    query = sa.select(User).where(User.username == username)
    user = db.first_or_404(query)
    form = EmptyForm()
    posts = db.session.scalars( current_user.following_posts() ).all()

    return render_template('user.html', user=user, posts=posts, form = form)


@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm( current_user.username )
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('changes saved'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title = 'edit profile', form= form)   

#follow
@app.route('/follow/<username>', methods=["POST"])
@login_required

def follow(username):
    form = EmptyForm()
    if form.validate_on_submit:
        query = sa.select(User).where(User.username == username)
        followed_user = db.session.scalar(query)
        if followed_user is None:
            flash(f'User {username} not found!')
            return redirect(url_for('index'))
        if followed_user == current_user:
            flash(f"You can't follow yourself chief hau!")
            return redirect('user', username = username)
        current_user.follow(followed_user)
        db.session.commit()
        flash(f'You now following {username}.')
        return redirect(url_for('user', username = username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=["POST"])
@login_required

def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        query = sa.select(User).where(User.username == username)
        Unfollowed_user = db.session.scalar(query)
        if Unfollowed_user is None:
            flash(f'user {username} not found!')
            return redirect(url_for('index'))
        if Unfollowed_user == current_user :
            flash(f'How can you possibly unfollow yourself chief?')
            return redirect('user', username = username)
        current_user.unfollow(Unfollowed_user)
        db.session.commit()
        flash(f'you unfollowed {username}')
        return redirect(url_for('user', username = username))
    else:
        return redirect('index')

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type= int)
    query = sa.select(Post).order_by( Post.timestamp.desc() )
    posts = db.paginate(query, page=page, per_page=app.config['POST_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page= posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page= posts.prev_num) \
        if posts.has_prev else None    
    return render_template('index.html', posts=posts.items, title = 'explore', next_url = next_url, prev_url= prev_url)    

@app.route('/reset_password_request', methods=['GET', 'POST'])
#this views function is resaponseble for rendering a form where the user can type their password. 
#also if is a post request then, send email to the given email. 
def reset_password_request():
    # check if the user is not logged.
    if current_user.is_authenticated:
        return redirect( url_for('index') )
    #make form instance.
    form = password_reset_request()
    if form.validate_on_submit():
        #we get the user with that email. 
        query = sa.select(User).where(User.email == form.email.data )
        user = db.session.scalar(query)
        if user :
             #if the user exist, we send them an email 
             send_password_reset_request_email(user)
             print('user exist')
        flash('Check your emails for futher instructions.')
        return redirect('reset_password_request')
     

    return render_template('reset_password_request.html', form= form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        print('user authenticated')
        return redirect(url_for('index'))
    user = User.verify_token(token)
    print(user)
    if not user:
        print('failed verifying the token')
        return redirect(url_for('index'))
    form = Reset_Password()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password is successfully changed')
        print('password changed')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, title = 'reset password', token = token)
