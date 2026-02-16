# SmartTask_Manager
Smart Task Management System
A backend-focused, multi-user task management application built with Flask, designed to handle deadline-aware tasks and automated email reminders using background schedulers.
This project goes beyond a basic todo app by implementing real-world backend concepts such as background jobs, time-based workflows, user isolation, and SMTP email automation.
<br>
Features
<br>
	• 🔐 User authentication (Register / Login / Logout)
	• 👤 Multi-user task isolation (each user sees only their tasks)
	• 🗓️ Create tasks with priority, status, and due date
	• ⏰ Background scheduler checks upcoming deadlines automatically
	• 📧 Email reminders sent before task due dates
	• 🔎 Filter tasks by priority and status
	• 🗄️ PostgreSQL database with SQLAlchemy ORM
	• 🔄 Database migrations using Flask-Migrate
<br>
Tech Stack
<br>
	• Backend: Python, Flask
	• Database: PostgreSQL, SQLAlchemy
	• Scheduler: APScheduler
	• Email Service: Flask-Mail (SMTP)
	• Auth & Security: Flask sessions
	• Frontend: HTML, CSS (Jinja templates)
<br>
System Design Overview<br>
	1. Users register and log in securely
	2. Tasks are stored with metadata (priority, status, due date, user_id)
	3. APScheduler runs a background job every 24 hours
	4. The scheduler:
		○ Scans pending tasks
		○ Calculates remaining days
		○ Triggers email reminders when deadlines approach
	5. Emails are sent dynamically to the task owner
	<br>
Installation & Setup
# Clone the repository
git clone https://github.com/your-username/smart-task-manager.git
cd smart-task-manager
# Create virtual environment
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Configure environment variables (Email & DB)
# Run database migrations
flask db upgrade
# Run the application
python app.py
<br>
Key Learnings
<br>
	• Implemented background schedulers for time-based automation
	• Integrated SMTP email systems with authentication handling
	• Designed scalable relational database models
	• Debugged real-world issues like async jobs, email failures, and migrations
<br>
 Future Improvements
	• Celery + Redis for scalable background jobs
	• REST API version of the backend
	• React frontend
	• Dockerization
<br>
 Author
 <br>
Prajukta Panda
<br>
Backend Developer | Python | Flask

