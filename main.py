from flask import Flask, request, redirect, render_template, flash, session
import re
from app import app, db
from models import User, Blog
from hashutils import check_pw_hash
from config import POSTS_PER_PAGE

app.secret_key = 'b6d2d1c83bcc4d09985fa319e9837c4053d87a99673eab9c204e38f0b395b0b0,QmJne'

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    username_error = ''
    password_error=''
    verify_error=''
    existing_user = User.query.filter_by(username=username).first()
    # Check for any username, password, verify or existing user errors
    if re.search(r"\s+", username):
        username_error = "That's not a valid username"
    elif re.search(r"^.{0,2}$", username):
        username_error = "That username is too short"
    elif existing_user:
        username_error = "That username already exist"
    if username_error:
        flash(username_error, 'error')
    if re.search(r"\s+", password):
        password_error = "That's not a valid password"
    elif re.search(r"^.{0,2}$", password):
        password_error = "That password is too short"
    if password_error:
        flash(password_error, 'error')
    if verify != password:
        verify_error = "Passwords don't match"
        flash(verify_error, 'error')
    # If there is no errors than login and add a session and add the info to a database
    if not existing_user and not username_error and not password_error and not verify_error:
        new_user = User(username, password)   #41-43 
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash("Logged in!")
        return redirect('/newpost')
    else:
        return render_template('signup.html', username=username)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    # Check if the user and password are correct to login
    username = request.form['username']
    password = request.form['password']
    username_error = ''
    password_error = ''
    user = User.query.filter_by(username=username).first()
    if user and check_pw_hash(password, user.pw_hash):
        session['username'] = user.username
        flash("Logged in!")
        return redirect('/newpost')
    elif user and not check_pw_hash(password, user.pw_hash):
        password_error = 'User password incorrect'
        flash(password_error, 'error')
    elif not user:
        username_error = 'User does not exist'
        flash(username_error, 'error')
    return render_template('login.html', username=username)
    
@app.route('/blog', methods=['POST', 'GET'])
@app.route('/blog/<int:page>', methods=['GET', 'POST'])
def blog(page=1):
    if request.method == 'GET':
        blog_id = request.args.get('id')
        user_id = request.args.get('user')
        # If id query is not none, it will create a page for the specfic blog post
        if blog_id:
            blog = Blog.query.filter_by(id=blog_id).first()
            return render_template('blog_id.html', blog=blog)
        # If user query is not none, it will create a page for the blog post for the specfic user
        elif user_id:
            owner = User.query.filter_by(id=user_id).first()
            blogs = Blog.query.filter_by(owner=owner).order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)#instead of paginate/ all
            return render_template('blog_user.html', owner=owner, blogs=blogs)
        else:
        # Create a blog page for all the blog post
            blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)#instead of paginate/ all
            return render_template('blog.html', title="Build a Blog", blogs=blogs)
    title_error = ''
    body_error = ''
    # Check if the title and content of the blog are not empty
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']
    blogs = Blog.query.all()
    if blog_title is '':
        title_error = "That's not a valid title"
        flash(title_error, 'error')
    if blog_body is '':
        body_error = "That's not a valid blog"
        flash(body_error, 'error')
    # Create a new post in the database and bring you to the new blog post
    if not title_error and not body_error:
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = new_blog.id
        return redirect('/blog?id={0}'.format(blog_id))
    else:
        # Return to the newpost page with errors and content that already been written
        return render_template('newpost.html', title="Add Blog Entry", blog_title=blog_title, blog_body=blog_body)

@app.route('/index')
def index():
    # Create a page for all the user that exist
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost')
def newpost():
    # Create a page for creating new post
    return render_template('newpost.html', title="Add Blog Entry")

@app.route('/logout')
def logout():
    # Logout of the account and delete the session 
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    # Allow to go to specfic page without being required to be login 
    allowed_routes = ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

if __name__ == '__main__':
    app.run()