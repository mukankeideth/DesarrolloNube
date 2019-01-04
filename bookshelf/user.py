# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bookshelf import get_model, cryptography
from flask import Blueprint, redirect, render_template, request, url_for, flash, session
from wtforms import Form, TextField, PasswordField, validators, StringField, SubmitField
import os
from bson.objectid import ObjectId

user = Blueprint('user', __name__)

# Variable to check logged user
log_user = None

## Classes for the forms
class LoginForm(Form):
    email = TextField('Email:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required()])

class RegisterForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required()])
    pass1 = PasswordField('Password:', validators=[validators.required()])
    pass2 = PasswordField('Repass:', validators=[validators.required()])

class SearchForm(Form):
    chain = TextField('Chain:', validators=[validators.required()])

## [BEGIN]
# Users log logic

#Function called before accessing any protected function
@user.before_request
def before_request():
    global log_user 
    log_user = None

    if 'user' in session:
        log_user = session['user']
    else:
        redirect(url_for("crud.list"))

    
    

@user.route('/login', methods=['GET','POST'])
def login():
    global log_user
    
    if log_user is not None:
        return redirect(url_for("crud.list"))

    form = LoginForm(request.form)
 
    if request.method == 'POST':
        if form.validate():
            # Log valid
            result = get_model().find_user_email(request.form['email'])
            if result is None:
                flash("Email is not valid. ")
            
            elif not cryptography.check_pass(request.form['password'], result['password']):
                flash("Password is incorrect")
            
            else:
                session['user'] = request.form['email']
                print(session)
                print(session['user'])
                return redirect(url_for('crud.list'))

        else:
            flash('All the form fields are required. ')
 
    return render_template('login.html', form=form)

# Logout function
@user.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('crud.list'))

# Check if the user is logged in
@user.route('/cheksess')
def check_session():
    if 'user' in session:
        return session['user']
    return None

# Register function
@user.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm(request.form)
 
    if request.method == 'POST':
        if form.validate():
            # Register successfully
            # We add the user to the database
            data = {}
            data['name'] = request.form['name']
            data['email'] = request.form['email']
            data['password'] = cryptography.encrypt_pass(request.form['pass1'])
            result = get_model().create_user(data)
            print(result)
            return redirect(url_for('user.login'))
        else:
            flash('All the form fields are required.')

    return render_template('signup.html', form=form)


## [END Users Log Logic]
@user.route('/<id>')
def view_user(id):
    user = get_model().read_user(id)
    return render_template("user.html", user=user)


# [START add]
@user.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        user = get_model().create_user(data)

        return redirect(url_for('crud.list'))

    return render_template("user_form.html", action="Create new user", user={})
# [END add]


@user.route('/<id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    user = get_model().read_user(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        user = get_model().update_user(data, id)

        return redirect(url_for('crud.list'))

    return render_template("user_form.html", action="Edit user", user=user)


@user.route('/<id>/delete')
def delete(id):
    get_model().delete_user(id)
    return redirect(url_for('crud.list'))
