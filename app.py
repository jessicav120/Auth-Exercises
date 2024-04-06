from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_exc"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "kikostinks"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def home_page():
    '''show home page'''
    
    return redirect('/register')

#----------------- Auth. Routes ---------------------
@app.route('/register', methods=["GET", "POST"])
def register_user():
    '''Show registration form & handle form submission
    If username is in session, do not allow access'''
    form = RegistrationForm()
    
    #if user IS logged in, deny acccess 
    if "username" in session:
        flash("You don't have permssion to do that", 'warning')
        return redirect(f'/users/{session["username"]}')
    
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "password": form.password.data,
            "email": form.email.data,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data
        }
        
        new_user = User.register(**data)
        
        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        
        flash("Registration Successful.", 'success')
        return redirect(f'/users/{new_user.username}')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def handle_login():
    '''show login form and handle submission'''
    form = LoginForm()
    #if user is logged in, deny acccess 
    if "username" in session:
        flash("You're already logged in", 'info')
        return redirect(f'/users/{session["username"]}')
    
    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        u = User.authenticate(username, pwd)
        
        if u:
            flash(f"Welcome back, {u.username}!", "info")
            session["username"] = u.username
            return redirect(f'/users/{session["username"]}')
        else:
            form.password.errors = ['Username or password is invalid.']
            
    return render_template('login.html', form=form)

@app.route('/logout', methods=["POST"])
def logout_user():
    '''remove username from session'''
    session.pop("username")
    return redirect('/login')
#------------------------------------------------------------------------------

# -------- USERS Routes ----------------
@app.route('/users/<username>')
def show_user(username):
    '''show user details page and their feedback posts.'''
    
    #if not logged in, deny access   
    if "username" not in session:
        flash("Log in to view.", "info")
        return redirect('/login')
    
    user = User.query.get_or_404(username)
    posts = user.posts
    return render_template('user_profile.html', user=user, posts=posts)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    '''delete user and their feedback from db and redirect'''
    
    if "username" not in session:
        flash("To do that, please log in", "info")
        return redirect('/login')
    elif session["username"] != username:
        flash("You don't have permssion to do that", "warning")
        return redirect(f'/users/{session["username"]}')
    
    user = User.query.get_or_404(username)
   
    if user.username == session["username"]:
        session.pop("username")
        db.session.delete(user)
        db.session.commit()
        flash("Profile deleted", "danger")
        return redirect('/')

#---------- FEEDBACK Routes ------------------------------------------------
@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    '''
    show form for adding feedback and handle its submission.
    Creates new feedback instance .
    '''
    form = FeedbackForm()
    
    #if not logged in, or incorrect user - prevent access
    if "username" not in session:
        flash("To do that, please log in", "info")
        return redirect('/login')
    elif session["username"] != username:
        flash("You don't have permssion to do that", "warning")
        return redirect(f'/users/{session["username"]}')
    
    if form.validate_on_submit():
        data = {
            "title": form.title.data,
            "content": form.content.data,
            "username": username
        }
        
        new_post = Feedback(**data)
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Feedback sent!', 'success')
        return redirect (f'/users/{username}')
    
    return render_template('add_feedback.html', form=form, username=username)

@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_feedback(id):
    '''update a feedback post '''
    post = Feedback.query.get_or_404(id)
    username = post.user.username 
    form = FeedbackForm(obj=post)
    
    #if not logged in, or incorrect user - prevent access
    if "username" not in session:
        flash("To do that, please log in", "info")
        return redirect('/login')
    elif session["username"] != username:
        flash("You don't have permssion to do that", "warning")
        return redirect(f'/users/{session["username"]}')
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        db.session.commit()
        
        return redirect(f'/users/{username}')
    
    return render_template('edit_feedback.html', form=form, post=post, username=username)

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    '''delete feedback instance'''
    
    if "username" not in session:
        flash("To do that, please log in", "info")
        return redirect('/login')
    
    post = Feedback.query.get(id)
    
    if post.username == session["username"]:
        db.session.delete(post)
        db.session.commit()
        flash("Feedback deleted", "secondary")
        return redirect(f'/users/{session["username"]}')
    
    flash("You don't have permission to do that", "warning")
    return redirect(f'/users/{session["username"]}')