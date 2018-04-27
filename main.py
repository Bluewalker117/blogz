from flask import Flask, request, redirect, render_template, flash, session
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
    user_id = db.Column(db.Integer, db.ForeignKey('User.id')) 


    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')


    def __init__(self, username, password):
        self.username = username
        self.password = password

def valid_length(text):    
    if 2 < len(text) < 21:
        return True
    else:
        return False 

def validate_password(password, password_2):
    if (password) == (password_2):
        return True
    else:
        return False


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        user2 = User.query.filter_by(username = user).first()
        
        if user2 and user2.password == password:
            session['user'] = user
            flash("Logged In")
            return redirect('/newpost')
        if user2 == None:
            flash('This user has not been registered')
            return redirect('/login')
        else:
            flash('User name or password is incorrect')
    return render_template('login.html')

@app.route("/logout", methods = ['GET'])
def logout():
    del session['user']
    return redirect('/')

@app.before_request
def login_required():
    allowed_routes = ["login", "signup", "blog", "index", "show_users", "user_display"]
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route("/index", methods=['GET'])
def show_users():
    y= request.args.get('id')
    x= User.query.all()
    return render_template('index.html', users=x) 


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nuser = request.form['user_name']
        npassword = request.form['new_password']
        vpassword = request.form['verify_password']

        nuser_error = ""
        npassword_error = ""
        vpassword_error = ""

        u_space_c = nuser.count(" ")
        p_space_c = npassword.count(" ")
    
        if nuser.strip()=="":
            nuser_error = "No"
            return render_template("signup.html", user_name_error = "Please enter a user name.")
        if u_space_c > 0:
            nuser_error = "No"
            return render_template("signup.html", user_name = nuser, user_name_error = 
        "You cannot have spaces in your user name.  Please try a new name.")
        else:
            nuser = nuser
            if valid_length(nuser)== False:
                nuser_error = "No"
                return render_template("signup.html", user_name = nuser, user_name_error = 
        "The name you have entered is not the required 3-20 characters in length.  Please try a new name.")

        if npassword.strip()=="":
            npassword_error = "No"
            return render_template("signup.html", user_name = nuser, new_password_error = 
        "Please enter a password.")
        if p_space_c > 0:
            npassword_error = "No"
            return render_template("signup.html", user_name = nuser, new_password_error = 
        "You cannot have spaces in your password. Please enter a password.")
        else:
            npassword = npassword
            if valid_length(npassword)== False:
                npassword_error = "No"
                return render_template("signup.html", user_name = nuser, new_password_error = 
        "The password you have entered is not the required 3-20 characters in length.  Please try a new password.")

        if vpassword.strip()=="":
            vpassword_error = "No"
            return render_template("signup.html", user_name = nuser, verify_password_error = 
        "Please re-enter your password for verification.")
        else:
            npassword = npassword
            vpassword = vpassword
            if validate_password(npassword, vpassword)==False:
                vpassword_error = "No"
                return render_template("signup.html", user_name = nuser, verify_password_error =
        "Your passwords did not match.")

        if not nuser_error and not npassword_error and not vpassword_error:
            existing_user = User.query.filter_by(username = nuser).first()
            if not existing_user:
                new_user = User(nuser, npassword)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = nuser
                return redirect('/newpost')
            else:
                flash("User already exists")
    
    return render_template('signup.html')


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
            user = User.query.filter_by(username=session['user']).first()
            new_blog = Blog(blog_title, blog_body, user)
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
    z= User.query.get(y)
    return render_template('blog_display.html', blog=x, user=z)   

@app.route("/singleuser/", methods=["GET"])
def user_display():
    y= request.args.get('id')
    x= Blog.query.filter_by(user_id=y)
    z= User.query.filter_by(id=y).first()
    return render_template('singleuser.html', blogs=x, user=z) 

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect("/blog")

app.secret_key = 'key'

if __name__ == '__main__':
    app.run() 