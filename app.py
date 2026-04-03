# app.py

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from models import db, bcrypt, User, College, Event
import os
import click

# --- APP CONFIGURATION ---
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt.init_app(app)

# --- DATABASE COMMANDS ---
@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Initialized the database.")

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
def create_admin_command(email, password):
    if User.query.filter_by(email=email).first():
        print(f"Error: User with email {email} already exists.")
        return
    admin_user = User(fullname="Admin", email=email, is_admin=True)
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin user {email} created successfully.")

# --- API ENDPOINTS ---
# == AUTHENTICATION ==
@app.route("/api/signup", methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409
    new_user = User(fullname=data['fullname'], email=data['email'], is_admin=False)
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route("/api/login", methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        return jsonify({"message": "Login successful", "user": {"fullname": user.fullname, "email": user.email}}), 200
    return jsonify({"message": "Invalid email or password"}), 401

@app.route("/api/admin-login", methods=['POST'])
def admin_login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')) and user.is_admin:
         return jsonify({"message": "Admin login successful"}), 200
    return jsonify({"message": "Invalid credentials or not an admin"}), 401

# == COLLEGES ==
@app.route("/api/colleges", methods=['GET'])
def get_colleges():
    colleges = College.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in colleges])

@app.route("/api/colleges", methods=['POST'])
def add_college():
    data = request.get_json()
    new_college = College(name=data['name'])
    db.session.add(new_college)
    db.session.commit()
    return jsonify({"id": new_college.id, "name": new_college.name}), 201

@app.route("/api/colleges/<int:college_id>", methods=['DELETE'])
def delete_college(college_id):
    college = College.query.get_or_404(college_id)
    db.session.delete(college)
    db.session.commit()
    return jsonify({"message": "College deleted successfully"}), 200

# == EVENTS ==
@app.route("/api/events/<int:event_id>", methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted successfully"}), 200

@app.route("/api/events", methods=['POST'])
def create_event():
    if 'permissions' not in request.files:
        return jsonify({"message": "Permission file is required"}), 400
    file = request.files['permissions']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_event = Event(
            name=request.form['name'],
            domain=request.form['domain'],
            registration_link=request.form['registrationLink'],
            college_id=request.form['collegeId'],
            status='pending',
            permission_filename=filename
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({"message": "Event submitted for approval!", "id": new_event.id}), 201
    return jsonify({"message": "File upload failed"}), 400

# --- MODIFIED: This function now correctly filters for approved events ---
@app.route("/api/colleges/<int:college_id>/events", methods=['GET'])
def get_events_for_college(college_id):
    college = College.query.get_or_404(college_id)
    # Only get approved events for this college
    approved_events = [e for e in college.events if e.status == 'approved']
    return jsonify([{"id": e.id, "name": e.name, "domain": e.domain, "registrationLink": e.registration_link} for e in approved_events])

@app.route("/api/events", methods=['GET'])
def get_all_events():
    events = Event.query.filter_by(status='approved').order_by(Event.id.desc()).all()
    results = []
    for event in events:
        results.append({
            "id": event.id, "name": event.name, "domain": event.domain,
            "registrationLink": event.registration_link, "collegeName": event.college.name
        })
    return jsonify(results)

# == ADMIN ROUTES ==
@app.route("/api/events/all-for-admin", methods=['GET'])
def get_all_events_for_admin():
    events = Event.query.order_by(Event.id.desc()).all()
    results = []
    for event in events:
        results.append({
            "id": event.id, "name": event.name, "status": event.status,
            "collegeName": event.college.name, "permission_filename": event.permission_filename
        })
    return jsonify(results)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/events/<int:event_id>/approve", methods=['POST'])
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = 'approved'
    db.session.commit()
    return jsonify({"message": "Event approved"})

@app.route("/api/events/<int:event_id>/reject", methods=['POST'])
def reject_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Event rejected"})

# == SEARCH ==
@app.route("/api/search", methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    # Search only approved events
    event_results = Event.query.filter(Event.name.ilike(f'%{query}%'), Event.status == 'approved').all()
    college_results = College.query.filter(College.name.ilike(f'%{query}%')).all()
    results = {
        "events": [{"id": e.id, "name": e.name, "college_id": e.college_id, "collegeName": e.college.name, "domain": e.domain, "registrationLink": e.registration_link} for e in event_results],
        "colleges": [{"id": c.id, "name": c.name} for c in college_results]
    }
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)