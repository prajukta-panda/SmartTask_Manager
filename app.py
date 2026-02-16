from flask import Flask , render_template, redirect, request,url_for,jsonify,make_response
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
#import jwt
#import uuid
from flask_migrate import Migrate
from datetime import datetime, timezone, timedelta
#from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity,unset_jwt_cookies
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://my_db_user:mypassword@localhost:5432/my_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["JWT_SECRET_KEY"] = "super-secret-key"
#cookies based JWT
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "jwt_token"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # for learning
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your_email@gmail.com',
    MAIL_PASSWORD='tgjvbzfmvuaitswl',
    MAIL_DEFAULT_SENDER='your_email@gmail.com'
    )



db = SQLAlchemy(app)
bcrypt =Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
mail = Mail(app)
scheduler = BackgroundScheduler()


class User(db.Model):
    __tablename__ = "users"
    id= db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password=db.Column(db.String(200),nullable=False)
    todos = db.relationship("Todo", backref="user", lazy=True)
class Todo(db.Model):
    __tablename__ = "todos"
    id= db.Column(db.Integer, primary_key=True)
    content= db.Column(db.String(50), nullable=False)
    #completed= db.Column(db.Boolean, default=False)
    status = db.Column(db.String(10), default="pending")
    priority = db.Column(db.String(10), default="Low")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False)


@app.route('/')
def home(): return render_template('login.html')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid email or password'}), 401
        access_token = create_access_token(identity=str(user.id))
        #refresh_token = create_refresh_token(identity=str(user.id))
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('jwt_token', access_token)
        return response
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'User already exists. Please login.'}), 400
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name,email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/dashboard')
@jwt_required()
def dashboard():
        current_user_id = int(get_jwt_identity())
        priority = request.args.get("priority")
        #completed = request.args.get("completed")
        status = request.args.get("status")

        query= Todo.query.filter_by(user_id=current_user_id)

        if priority:
            query=query.filter_by(priority=priority)
        '''if completed is not None:
          query = query.filter_by(completed=(completed == "true"))'''
    
        '''if completed in ["True", "False"]:
            query = query.filter(Todo.completed == (completed == "True"))'''
        if status in ["pending", "completed"]:
             query = query.filter(Todo.status == status)

        tasks= query.all()
        user = User.query.get(current_user_id)
        print(f"Hello user {user.name}! You are logged in.")
        return render_template('dashboard.html', tasks=tasks , user=user)
   
@app.route('/add-task', methods=['POST'])
@jwt_required()
def add_task():
    task_content = request.form['content']
    priority = request.form.get("priority", "Low")
    #completed = request.form.get("completed") == "True"
    #completed = bool(request.form.get("completed","False"))
    ''' completed_raw = request.form.get("completed", "False")
    completed = True if completed_raw.lower() == "true" else False'''
    status = request.form.get("status", "pending")

    user_id = int(get_jwt_identity())
    due_date_str = request.form.get('due_date')
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None

    new_task = Todo(
        content=task_content,
        priority=priority,
        user_id= user_id,
        due_date=due_date,
        status=status,
        #completed=completed
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
@jwt_required()
def delete(id):
     user_id = int(get_jwt_identity())
     task_to_delete = Todo.query.filter_by(id=id, user_id=user_id).first_or_404()

     try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/dashboard')

     except:
        return 'There is a problem in deleting'

@app.route('/update/<int:id>', methods=['POST','GET'])
@jwt_required()
def update(id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    #task = Todo.query.get_or_404(id)
    task = Todo.query.filter_by(id=id, user_id=user_id).first_or_404()    
    if request.method == 'POST':
        task.content= request.form['content']
        task.priority = request.form.get("priority", "Low")
        #task.completed = request.form.get("completed") == "True"
        #task.completed = bool(request.form.get("completed","False"))
        task.status = request.form.get("status", "pending")

        try:
            db.session.commit()
            return redirect('/dashboard')

        except:
            return 'There is a problem in updating'        

    else:
         return render_template('update.html', task=task,user=user)  
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    unset_jwt_cookies(response)
    return response     


#Email sending function
def send_reminder_email(user_email, task, days_left):
    subject = f"⏰ Task Reminder: {task.content}"
    body = f"""
Hello,

Your task "{task.content}" is due in {days_left} day(s).

Due Date: {task.due_date.strftime('%Y-%m-%d')}
Priority: {task.priority}

Please complete it on time.

— Smart Task Manager
"""

    msg = Message(subject, recipients=[user_email], body=body)
    mail.send(msg)
#Reminder job
def check_due_tasks():
    print("🔍 Checking due tasks...")

    with app.app_context():
        now = datetime.utcnow()

        tasks = Todo.query.filter(
            Todo.status == "pending",
            Todo.due_date != None
        ).all()

        print("📌 Found tasks:", len(tasks))

        for task in tasks:
            days_remaining = (task.due_date.date() - now.date()).days
            print(f"🕒 Task {task.id} days remaining:", days_remaining)

            if days_remaining in (1, 2):
                user = User.query.get(task.user_id)
                print("📧 Sending email to:", user.email)
                send_reminder_email(user.email, task, days_remaining)


if __name__ == "__main__":
    scheduler.add_job(check_due_tasks, 'interval', hours=24)
    scheduler.start()
    app.run(debug=True,use_reloader=False)  
 