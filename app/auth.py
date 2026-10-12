from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select
from .extensions import db
from .models import Member
auth_bp=Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        name=request.form.get('full_name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password',''); confirm=request.form.get('confirm_password','')
        errors=[]
        if not name or len(name)>150: errors.append('Enter a name up to 150 characters.')
        if not email or len(email)>254 or '@' not in email: errors.append('Enter a valid email.')
        if len(password)<12: errors.append('Password must be at least 12 characters.')
        if password!=confirm: errors.append('Passwords do not match.')
        if db.session.scalar(select(Member).where(Member.email==email)): errors.append('An account with that email already exists.')
        exp=request.form.get('experience_years','').strip(); experience=None
        if exp:
            try:
                experience=float(exp)
                if not 0<=experience<=80: raise ValueError()
            except ValueError: errors.append('Experience must be between 0 and 80 years.')
        if errors:
            for e in errors: flash(e,'error')
            return render_template('register.html'),400
        m=Member(full_name=name,email=email,phone=request.form.get('phone','').strip() or None,city=request.form.get('city','').strip() or None,skills=request.form.get('skills','').strip() or None,experience_years=experience)
        m.set_password(password); db.session.add(m); db.session.commit(); login_user(m)
        flash('Registration successful. You can now upload documents.','success'); return redirect(url_for('main.dashboard'))
    return render_template('register.html')
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        m=db.session.scalar(select(Member).where(Member.email==email))
        if m and m.check_password(password): login_user(m); return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.','error')
    return render_template('login.html')
@auth_bp.post('/logout')
def logout():
    logout_user(); flash('Signed out.','success'); return redirect(url_for('main.index'))
