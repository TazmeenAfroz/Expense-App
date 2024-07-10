from flask import Flask, render_template, request, flash, redirect, session, url_for
import mysql.connector
import os
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import date
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['WTF_CSRF_SSL_STRICT'] = False

csrf = CSRFProtect(app)

class ExpenseForm(FlaskForm):
    date = StringField('Date', default=date.today())
    category = SelectField('Category', choices=[('Food', 'Food'), ('Transport', 'Transport'), ('Shopping', 'Shopping'), ('Rent', 'Rent'), ('Others', 'Others')])
    amount = StringField('Amount')
    notes = StringField('Notes')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email')
    password = StringField('Password')
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email')
    password = StringField('Password')
    submit = SubmitField('Submit')

class EarningForm(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SettingsForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email')
    password = StringField('Password')
    submit = SubmitField('Submit')





try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="expense_DB"
    )
    cursor = conn.cursor()
    print("Connected")
except mysql.connector.Error as e:
    print("Error code:", e.errno)        # error number
    print("SQLSTATE value:", e.sqlstate)
    print("Error message:", e.msg)       # error message
    print("Error:", e)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/')

    user_id = session['user']

    cursor.execute("SELECT SUM(amount) FROM earnings WHERE user_id = %s", (user_id,))
    total_earning = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = %s", (user_id,))
    total_expense = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
    expenses = cursor.fetchall()

    balance = total_earning - total_expense

    expense_form = ExpenseForm()

    return render_template('home.html', total_earning=total_earning, total_expense=total_expense, balance=balance, recent_expenses=expenses, form=expense_form)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user' in session:
        form = ExpenseForm()
        if form.validate_on_submit():
            user_id = session['user']
            category = form.category.data
            amount = form.amount.data
            notes = form.notes.data
            date = form.date.data

            cursor.execute("SELECT SUM(amount) FROM earnings WHERE user_id = %s", (user_id,))
            total_earning = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = %s", (user_id,))
            total_expense = cursor.fetchone()[0] or 0

            balance = total_earning - total_expense
            if balance < int(amount):
                flash('Cannot add expense. Insufficient balance', 'danger')
            else:
                cursor.execute("INSERT INTO expenses (user_id, category, amount, notes, date) VALUES (%s, %s, %s, %s, %s)", (user_id, category, amount, notes, date))
                conn.commit()

                flash('Expense added successfully', 'success')
            return redirect('/home')
        else:
            flash('Error adding expense. Please check your inputs.', 'danger')
            return redirect('/home')
    else:
        flash('Please login to add expenses', 'danger')
        return redirect('/')

@app.route('/')
def login():
    form = LoginForm()
    if 'user' in session:
        return redirect('/home')
    return render_template('login.html', form=form)

@app.route('/register')
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)


@app.route('/loginvalidation', methods=['POST', 'GET'])
def loginvalidation():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user'] = user[0]
            flash('You have been logged in successfully', 'success')
            return redirect('/home')
        else:
            flash('Invalid email or password', 'danger')
            return redirect('/')
    flash('Invalid form submission', 'danger')
    return redirect('/')

@app.route('/registeruser', methods=['POST'])
def registeruser():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        flash('User registered successfully', 'success')
        return redirect('/')
    flash('Error in registration', 'danger')
    return redirect('/register')

@app.route('/add_earning', methods=['POST', 'GET'])
def add_earning():
    if 'user' in session:
        form = EarningForm()
        if form.validate_on_submit():
            user_id = session['user']
            new_earning_amount = form.amount.data

            try:
                new_earning_amount = int(new_earning_amount)
            except ValueError:
                flash('Invalid amount format', 'danger')
                return render_template('home.html', form=form)

            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM earnings WHERE user_id = %s", (user_id,))
            current_total_earnings = cursor.fetchone()[0]

            updated_total_earnings = current_total_earnings + new_earning_amount

            cursor.execute("INSERT INTO earnings (user_id, amount) VALUES (%s, %s) ON DUPLICATE KEY UPDATE amount = %s", (user_id, updated_total_earnings, updated_total_earnings))
            conn.commit()

            flash('Earning added successfully', 'success')
            return redirect('/home')
        else:
            flash('Error adding earnings', 'danger')
            return render_template('home.html', form=form)
    else:
        flash('Please log in to add earnings', 'danger')
        return redirect('/')
    


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' in session:
        user_id = session['user']
        
        
        cursor.execute("SELECT name, email FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        form = SettingsForm()
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data

            cursor.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s", 
                           (name, email, password, user_id))
            conn.commit()

            flash('Settings updated successfully', 'success')
            return redirect('/settings')
        
        form.name.data = user[0]  
        form.email.data = user[1]
        return render_template('settings.html', form=form, user={'name': user[0], 'email': user[1]})
    
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user' in session:
        user_id = session['user']
        
        # Fetch user details
        cursor.execute("SELECT name, email FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Fetch user's balance
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM earnings WHERE user_id = %s", (user_id,))
        total_earning = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = %s", (user_id,))
        total_expense = cursor.fetchone()[0]
        
        balance = total_earning - total_expense
        
        avatars = ['/static/avatars/avatar1.png', '/static/avatars/avatar2.png', '/static/avatars/avatar3.png']
        selected_avatar = random.choice(avatars)
        
        return render_template('profile.html', user={'name': user[0], 'email': user[1]}, avatar=selected_avatar, balance=balance)
    return redirect('/')

@app.route('/analysis')
def analysis():
    if 'user' in session:
        user_id = session['user']
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id = %s GROUP BY category", (user_id,))
        expenses_by_category = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(date, '%Y') as year, DATE_FORMAT(date, '%Y-%m') as month, SUM(amount)
            FROM expenses
            WHERE user_id = %s
            GROUP BY year, month
            ORDER BY year, month
        """, (user_id,))
        expenses_by_year_month = cursor.fetchall()

        return render_template('analysis.html', expenses_by_category=expenses_by_category, expenses_by_year_month=expenses_by_year_month)
    return redirect('/')



@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect('/')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        cursor.close()
        conn.close()
        print("Connection closed")
