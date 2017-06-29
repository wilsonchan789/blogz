from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:flask@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fkjafhsd&hew43'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        blog_id = request.args.get('id')
        if blog_id != None:
            blog = Blog.query.filter_by(id=blog_id).first()
            blog_title = blog.title
            blog_body = blog.body
            return render_template('blog_id.html', blog_title=blog_title, blog_body=blog_body)
        else:
            blogs = Blog.query.all()
            return render_template('blog.html', title="Build a Blog", blogs=blogs)
    title_error = ''
    body_error = ''
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']
    if blog_title is '':
        title_error = "That's not a valid title"
    if blog_body is '':
        body_error = "That's not a valid blog"
    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = new_blog.id
        return redirect('/blog?id={0}'.format(blog_id))
    else:
        return render_template('newpost.html', title="Add Blog Entry", blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)

@app.route('/newpost')
def newpost():
    return render_template('newpost.html', title="Add Blog Entry")

if __name__ == '__main__':
    app.run()