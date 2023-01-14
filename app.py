import re
from flask import Flask, render_template, request, redirect, session, send_file, jsonify
from flask.helpers import url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
import traceback


# Flask constructor takes the name of
# current module (_name_) as argument.
app = Flask(__name__)

HOST="ap-south.connect.psdb.cloud"
USERNAME="br6045py36xywpd224a5"
PASSWORD="pscale_pw_HaKKvTgmV1sUYWPJx7blGXbZAgVuR5T4lzs11f0axX5"
DATABASE="vjti-alumni"

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://shracker:pGc9NwyeELLcPI2077gF4YNPCFdPkxkk@dpg-cf0k0414reb56qk6mcbg-a.singapore-postgres.render.com/vjti_alumni"
# app.config["SQLALCHEMY_BINDS"] = {
#     "users": "sqlite:///users.db",
#     "events": "sqlite:///events.db",
# }
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config[
    "SECRET_KEY"
] = "hes,mnwiou42y34kkjbhjf6587876yghbjk$5iyiugu435e12354232452ghdsf3gef"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=8)
app.jinja_env.add_extension("jinja2.ext.do")
db = SQLAlchemy(app)
login = LoginManager(app)
@login.user_loader
def load_user(user_email):
    return Users.query.get(user_email)
app.config["SESSION_SQLALCHEMY"] = db

sess = Session(app)


# users = db.Table(
#     "users",
#     db.Column('user_email', db.String(100),primary_key=True),

# )


user_posts = db.Table(
    "user_posts",
    db.Column("postid", db.Integer, db.ForeignKey("posts.postid")),
    db.Column("user_email", db.String(100), db.ForeignKey("users.user_email"))
)



class program(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    users = db.relationship('Users', backref='program')
    branches = db.relationship('branch', backref='program')
    batches = db.relationship('batch', backref='program')
    def __repr__(self):
        return self.name



class branch(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    users = db.relationship('Users', backref='branch')
    program_name = db.Column(db.String(100), db.ForeignKey('program.name'))
    def __repr__(self):
        return self.name


class batch(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    users = db.relationship('Users', backref='batch')
    program_name = db.Column(db.String(100), db.ForeignKey('program.name'))
    def __repr__(self):
        return self.name


class Users(db.Model, UserMixin):
    # # __searchable__ = ['user', 'passwd']
    user_email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.BigInteger)
    location = db.Column(db.String(100))
    batch_name = db.Column(db.String(100), db.ForeignKey('batch.name'))
    branch_name = db.Column(db.String(100), db.ForeignKey('branch.name'))
    program_name = db.Column(db.String(100), db.ForeignKey('program.name'))
    reg_no = db.Column(db.Integer)
    is_member = db.Column(db.Boolean)
    # is_manager = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    comments = db.relationship('post_comments', backref='user')
    posts = db.relationship('posts', backref='user')

    def get_id(self):
        return self.user_email

    def __repr__(self):
        return self.name

def test_connection():
    with app.app_context():
        db.create_all()

class event_urls(db.Model):
    # __bind_key__ = "events"
    urlid = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    eventid = db.Column(db.Integer, db.ForeignKey('events.eventid'))
    def __repr__(self):
        return self.url


class post_urls(db.Model):
    # __bind_key__ = "events"
    urlid = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    postid = db.Column(db.Integer, db.ForeignKey('posts.postid'))
    def __repr__(self):
        return self.url


class event_reviews(db.Model):
    # __bind_key__ = "events"
    reviewid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    review = db.Column(db.String(2000), nullable=False)
    eventid = db.Column(db.Integer, db.ForeignKey('events.eventid'))
    def __repr__(self):
        return self.title



class post_comments(db.Model):
    # __bind_key__ = "events"
    commentid = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(2000), nullable=False)
    user_name = db.Column(db.String(100), db.ForeignKey('users.user_email'))
    postid = db.Column(db.Integer, db.ForeignKey('posts.postid'))
    def __repr__(self):
        return self.comment


class event_faqs(db.Model):
    # __bind_key__ = "events"
    faqid = db.Column(db.Integer, primary_key=True)
    que = db.Column(db.String(2000), nullable=False)
    ans = db.Column(db.String(2000), nullable=False)
    eventid = db.Column(db.Integer, db.ForeignKey('events.eventid'))
    def __repr__(self):
        return self.que


class events(db.Model):
    # __bind_key__ = "events"
    eventid = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String(100), nullable=False)
    event_description = db.Column(db.String(2000), nullable=False)
    register_start = db.Column(db.DateTime)
    register_end = db.Column(db.DateTime)
    event_start = db.Column(db.DateTime, nullable=False)
    event_end = db.Column(db.DateTime, nullable=False)
    result_date = db.Column(db.DateTime)
    urls = db.relationship('event_urls', backref='event')
    def __repr__(self):
        return self.event_title


class posts(db.Model):
    # __bind_key__ = "events"
    postid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    urls = db.relationship('post_urls', backref='post')
    comments = db.relationship('post_comments', backref='post')
    user_name = db.Column(db.String(100), db.ForeignKey('users.user_email'))
    likes = db.Column(db.Integer)
    def __repr__(self):
        return self.event_title

test_connection()



# class ManagerModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated and (current_user.is_manager or current_user.is_admin)

# class AdminModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.is_admin

# class NoEditModelView(ManagerModelView):
#     can_edit = False

# class UsersModelView(AdminModelView):
#    form_columns = ('user_email', 'name', 'password', 'mobile', 'location', 'current_class', 'roll_no', 'is_member', 'is_manager', 'is_admin')
#    column_list = ('user_email', 'name', 'password', 'mobile', 'location', 'current_class', 'roll_no', 'is_member', 'is_manager', 'is_admin')
#    column_exclude_list = ['password']


# class EventsModelView(NoEditModelView):
#     form_columns = ('event_title', 'event_description', 'register_start', 'register_end', 'event_start', 'event_end', 'result_date')
#     # form_widget_args = {
#     #     'register_start': {
#     #         'readonly': True
#     #     },
#     #     'register_end': {
#     #         'readonly': True
#     #     },
#     #     'event_start': {
#     #         'readonly': True
#     #     },
#     #     'event_end': {
#     #         'readonly': True
#     #     },
#     #     'result_date': {
#     #         'readonly': True
#     #     },
#     #     'event_description': {
#     #         'rows': 10,
#     #         'style': 'color: black'
#     #     }
#     # }
#     def _description_formatter(view, context, model, name):
#         # Format your string here e.g show first 20 characters
#         # can return any valid HTML e.g. a link to another view to show the detail or a popup window
#         return model.event_description[:20]

#     column_formatters = {
#         'event_description': _description_formatter,
#     }

# administrator = Admin(app)
# administrator.add_view(UsersModelView(Users, db.session))
# administrator.add_view(EventsModelView(events, db.session))
# administrator.add_view(ManagerModelView(event_urls, db.session))
# administrator.add_view(ManagerModelView(event_faqs, db.session))
# administrator.add_view(ManagerModelView(event_reviews, db.session))

# db.create_all()

# # The route() function of the Flask class is a decorator,
# # which tells the application which URL should call
# # the associated function.


@app.route("/events", methods=['GET','POST','PUT','DELETE'])
def events():
    if request.method == 'POST':
        try:
            input = request.get_json()
            urls = input['urls']
            obj = events(event_title=input['event_title'],event_description=input['event_description'],register_start=input['register_start'],register_end=input['register_end'],event_start=input['event_start'],event_end=input['event_end'])
            db.session.add(obj)
            for url in urls:
                n = event_urls(url = url, event = obj)
                db.session.add(n)
            return True
        except:
            print(traceback.print_exc())
    elif request.method == 'GET':
        try:
            eventid = request.args.get('eventid')
            event = events.query.get(eventid)
            urls = []
            for url in event.urls:
                urls.append(url.url)
            return jsonify({
               'event_title': event.event_title,
                'event_description': event.event_description,
                'register_start': event.register_start,
                'register_end': event.register_end,
                'event_start': event.event_start,
                'event_end': event.event_end,
                'urls': urls
            })
        except:
            print(traceback.print_exc())
            return False
    


# @app.route("/about")
# # ‘/’ URL is bound with hello_world() function.
# def about_page():
#     return render_template("ACTS FrontEnd/about.html", registered_users_count=len(Users.query.all()), event_count=len(events.query.all()))


# @app.route("/404")
# def error_page():
#     return render_template("ACTS FrontEnd/404.html")


# @app.route("/dashboard")
# # ‘/’ URL is bound with hello_world() function.
# def dashboard():
#     return render_template("Dashboard/index.html")


# @app.route("/edit-profile")
# def editprofile():
#     return render_template("Edit-Profile/editprofile.html")


# @app.route("/event-page/<eventid>")
# def eventpage(eventid):
#     event = events.query.filter_by(
#                     eventid=eventid).first()
#     name=event.event_title
#     print(event.event_title)
#     print(    event_start = db.Column(db.DateTime, nullable=False)
# .strftime("%b %d"))

#     return render_template("Event-Page/index.html", eventname=name, eventdesc="jdsfjn")

    
# @app.route("/events/<event_no>")
# def event_display(event_no):
#     event_no = int(event_no)
#     if event_no <= len(events.query.all()):
#         event = events.query.filter_by(eventid=event_no).first()
#         print(event)
#         return render_template("Event-Page/index.html", 
#             event_name=event.event_title, 
#             event_desc=event.event_description,
#             rs_date=event.register_start,
#             re_date=event.register_end,
#             s_time=event.event_start,
#             e_time=event.event_end,
#             r_date=event.result_date
#             )
#     else:
#         return redirect('/404')

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if not current_user.is_authenticated:
#         if request.method == 'POST':
#             email = request.form['email']
#             passwd = request.form['passwd']
#             db_len = len(Users.query.all())
#             user_right = False
#             pass_right = False
#             for i in range(db_len):
#                 if email == Users.query.all()[i].user_email:
#                     user_right = True
#                     if passwd == Users.query.all()[i].password:
#                         pass_right = True
#                         break
#             if user_right and pass_right:
#                 user = Users.query.get(email)
#                 if user.is_member:
#                 # if True:
#                     session['user'] = user
#                     login_user(user)
#                     if user.is_admin or user.is_manager:
#                         return redirect('/admin')
#                     else:
#                         return redirect('/')
#                 else:
#                     session['error'] = 'You are not a member yet!'             
#             else:
#                 session['error'] = 'Invalid Email/Password.'             
#         return render_template("ACTS FrontEnd/login.html")
#     else:
#         return redirect('/')

# @app.route("/register", methods=['POST'])
# def register():
#     if not current_user.is_authenticated:
#         name = request.form['name']
#         email = request.form['email']
#         passwd = request.form['passwd']
#         if(len(passwd)<7):
#             session['error'] = 'Password should be more that 7 digits.'            
#             return render_template("ACTS FrontEnd/login.html")
#         user_exists = Users.query.filter_by(
#                             user_email=email).first()
#         if user_exists:
#             session['error'] = 'Email Already in use. Please Login'   
#             return render_template("ACTS FrontEnd/login.html")
#         user = Users(user_email=email, name=name, password=passwd, is_member=False, is_manager=False, is_admin=False)
#         db.session.add(user)
#         db.session.commit()
#         session['success'] = 'Registered Successfully! Please Login.'
#         return render_template("ACTS FrontEnd/login.html")
#     else:
#         return redirect('/')

# @app.route("/logout")
# def logout():
#     if current_user.is_authenticated:
#         session.pop('user', None)
#         logout_user()
#     return redirect('/')

# @app.route("/manage-event")
# def manageevent():
#     return render_template("Manage-Event/ManageEvent.html")


# main driver function
if __name__ == "__main__":

    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)
