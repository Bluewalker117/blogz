from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

app.config['DEBUG'] = True  

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True) #will give a unique ID to each databse entry
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    #user_id = db.Column(db.Integer, db.ForeignKey('User.id')) 


    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    #blogs = db.relationship('Blog', backref='User_id')


    def __init__(self, username, password):
        self.username = username
        self.password = password




@app.route("/login", methods=['GET','POST'])


@app.route("/index", methods=['GET', 'POST'])

@app.route("/signup", methods=['POST', 'GET'])


@app.route("/newpost", methods=['GET','POST'])
def newpost():
    
    if request.method == 'POST':
        new_blog_body = request.form['blog_body']
        new_blog_title = request.form['blog_title']

        error= ""
                 
        if new_blog_title.strip()=="":
            error = "Your blog is not titled. It will need a title and a knighthood to be posted."
            return render_template("newpost.html", blog_body= new_blog_body, error=error)
        if new_blog_body.strip() == "":
            error = "Your blog is invisible. You can't read what you can't see.  Please add visible text."
            return render_template("newpost.html", blog_title= new_blog_title, error=error)
        if not error:
            blog_title = request.form['blog_title']
            blog_body = request.form['blog_body']
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            new = db.session.query(Blog).order_by(Blog.id.desc()).first()
            newb = str(new)
            x = newb[1:-1]
            z = x[5:]
            return redirect('/blog_display/?id=' + z)

    else:
        return render_template('newpost.html')

@app.route("/blog", methods=['GET'])
def blog():
    blogs = Blog.query.all()
    return render_template('blog_posts.html', blogs=blogs)
    
@app.route("/blog_display/", methods=['GET'])
def blog_display():
    y= request.args.get('id')
    x= Blog.query.get(y)
    return render_template('blog_display.html', blog=x)    

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog_posts.html', blogs=blogs)

app.secret_key = 'key'

if __name__ == '__main__':
    app.run() 