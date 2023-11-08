from flask import Flask, render_template, request, redirect, url_for, session , flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.secret_key = 'secret_key'  
app.config['INSTANCE_RELATIVE_CONFIG'] = False
db = SQLAlchemy(app)

class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    stem_bg =  db.Column(db.String(120), nullable=False)
    experience = db.Column(db.Integer(),  nullable=False)
    skills = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    bio = db.Column(db.String(1000),  nullable=False)

class Mentee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    stem_interest = db.Column(db.String(120), nullable=False)
    skills = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    bio = db.Column(db.String(1000),  nullable=False)
    
class ForumMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    message_content = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mentor/register', methods=['GET', 'POST'])
def mentor_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        stem_bg = request.form['stem_bg']
        experience = request.form['experience']
        skills = request.form['skills']
        website = request.form['website']
        bio = request.form['bio']

        # Create a new Mentor object and add it to the database
        mentor = Mentor(name=name, email=email, password=password, stem_bg=stem_bg, experience=experience, skills=skills, website=website, bio=bio)
        db.session.add(mentor)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('mentor_register.html')

@app.route('/mentee/register', methods=['GET', 'POST'])
def mentee_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        stem_interest = request.form['stem_interest']
        skills = request.form['skills']
        skills = ','.join([skill.strip().lower() for skill in skills.split(',')])
        website = request.form['website']
        bio = request.form['bio']

        # Create a new Mentee object and add it to the database
        mentee = Mentee(name=name, email=email, password=password, stem_interest=stem_interest, skills=skills, website=website, bio=bio)
        db.session.add(mentee)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('mentee_register.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # 'mentor' or 'mentee'

        # Check user credentials and set user_id in the session
        user = None
        if role == 'mentor':
            user = Mentor.query.filter_by(email=email, password=password).first()
        elif role == 'mentee':
            user = Mentee.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id  # Store user ID in the session
            session['user_name'] = user.name
            session['user_email'] = user.email
            
            
            if role == 'mentee':
                session['role'] = 'mentee'
                return redirect(url_for('search'))  # Display the search mentors template
            elif role == 'mentor':
                session['role'] = 'mentor'
                return redirect(url_for('mentor_profile'))
            

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/mentor_profile')
def mentor_profile():
    user = Mentor.query.filter_by(email=session.get('user_email')).first()
    return render_template('mentor_profile.html' , user = user)


@app.route('/my_profile')
def mentee_profile():
    user = Mentee.query.filter_by(email=session.get('user_email')).first()
    return render_template('mentee_profile.html' , user = user)

@app.route('/edit_mentee', methods=['GET','POST', 'PUT'])
def edit_mentee():
    user = Mentee.query.filter_by(email=session.get('user_email')).first()
    if request.method in ['POST','PUT']:
            
            # Check if the user exists
            if user:
                # Update the user's profile with the form data
                user.name = request.form['name']
                user.stem_interest = request.form['stem_interest']
                user.skills = request.form['skills']
                user.website = request.form['website']
                user.bio = request.form['bio']
                
                # Commit the changes to the database
                db.session.commit()
                
                # Redirect the user to their profile page or another appropriate page
                return redirect(url_for('mentee_profile'))
    
    # If any condition is not met, render the edit_mentee.html template
    return render_template('edit_mentee.html' , user = user)



@app.route('/edit_mentor', methods=['GET','POST', 'PUT'])
def edit_mentor():
    user = Mentor.query.filter_by(email=session.get('user_email')).first()
    if request.method in ['POST','PUT']:
            
            # Check if the user exists
            if user:
                # Update the user's profile with the form data
                user.name = request.form['name']
                user.stem_bg = request.form['stem_bg']
                user.experience = request.form['experience']
                user.skills = request.form['skills']
                user.website = request.form['website']
                user.bio = request.form['bio']
                
                # Commit the changes to the database
                db.session.commit()
                
                # Redirect the user to their profile page or another appropriate page
                return redirect(url_for('mentor_profile'))
    
    # If any condition is not met, render the edit_mentee.html template
    return render_template('edit_mentor.html' , user = user)


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    user = None
    role = None
    if Mentor.query.get(user_id):
        user = Mentor.query.get(user_id)
        role = 'mentor'
        
    elif Mentee.query.get(user_id):
        user = Mentee.query.get(user_id)
        role = 'mentee'
    
    if role == 'mentee':
        return render_template('search.html', user=user)  # Display the search mentors template
    elif role == 'mentor':
        return render_template('mentor_profile.html', user=user)
    

@app.route('/search')
def search():
    user = session.get('user_name')
    return render_template('search_mentors.html' , user =user)

    
@app.route('/search_results', methods=['GET'])
def search_mentors():
    user = session.get('user_name')
    field_of_expertise = request.args.get('field_of_expertise')
    skills = request.args.get('skills')

    # Create a base query
    query = Mentor.query

    # Create an empty list to hold filter conditions
    filter_conditions = []

    # Apply filters if provided
    if field_of_expertise:
        filter_conditions.append(Mentor.stem_bg == field_of_expertise)

    if skills:
        # Split the skills input and create filter conditions for each skill
        skills_list = [skill.strip().lower() for skill in skills.split(',')]
        skill_filters = [Mentor.skills.ilike('%' + skill + '%') for skill in skills_list]

        # Combine skill filters with an OR operator
        skill_condition = or_(*skill_filters)
        filter_conditions.append(skill_condition)

    # Combine all filter conditions with an AND operator
    if filter_conditions:
        query = query.filter(and_(*filter_conditions))

    # Execute the query to get filtered mentors
    mentors = query.all()
    
    if not mentors and field_of_expertise:
        mentors = Mentor.query.filter_by(stem_bg=field_of_expertise).all()

    return render_template('search_results.html', mentors=mentors , user = user )

@app.route('/contact_mentor/<int:mentor_id>', methods=['GET'])
def contact_mentor(mentor_id):
    # Retrieve the mentor with the given mentor_id and render the 'contact_mentor.html' template
    mentor = Mentor.query.get(mentor_id)
    user = session.get('user_name')
    if mentor:
        return render_template('contact_mentor.html', mentor=mentor , user = user)
    else:
        # Handle the case where the mentor with the provided ID does not exist
        flash('Mentor not found', 'danger')
        return redirect(url_for('search_results'))
    
    
@app.route('/forum')
def forum():
    user = session.get('user_name')
    messages = ForumMessage.query.order_by(ForumMessage.timestamp.desc()).all()
    role = session.get('role')
    if (role == 'mentee'):
        return render_template('Forum.html', messages=messages , home_url = '/search' , user = user)
    else:
        return render_template('Forum.html', messages=messages , home_url = '/mentor_profile' , user = user)
        

@app.route('/post_message', methods=['GET', 'POST'])
def post_message():
    if request.method == 'POST':
        
            role = session.get('role')
            email = session.get('user_email')
            name = session.get('user_name')
            message_content = request.form['message_content']

            message = ForumMessage(role=role, email=email, name=name, message_content=message_content)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('forum'))
    return render_template('post_message.html')
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
