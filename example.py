from random import randint
from flask import Flask, render_template, request, redirect, flash, \
    get_flashed_messages, url_for, session
import json

app = Flask(__name__)
app.secret_key = "secret_key"


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/courses')
def courses():
    return f'<a href="/courses/1">Course 1</a>'


@app.route('/courses/<id>')
def courses_id(id):
    return f'Course id: {id}'


@app.route('/users/<int:id>')
def get_user(id):
    with open('repo.json', 'r') as repo:
        read_repo = json.loads(repo.read())
        messages = get_flashed_messages(with_categories=True)
        for user in read_repo:
            if id == user['id']:
                return render_template('users/show.html', user=user,
                                       messages=messages)
            else:
                continue
        return 'User not found', 404


@app.get('/users')
def get_users():
    search_name = request.args.get('search_name', '')
    messages = get_flashed_messages(with_categories=True)
    with open('repo.json', 'r') as repo:
        filtered_names = filter(
            lambda user: search_name.lower() in user['nickname'].lower(),
            json.loads(repo.read()))
        return render_template('users/index.html', users=filtered_names,
                               search=search_name, messages=messages)


@app.get('/users/new')
def create_user():
    user = {'nickname': '',  'email': ''}
    errors = []
    return render_template('users/new.html', user=user, errors=errors)


@app.post('/users')
def create_user_post():
    with open('repo.json', 'r') as repo:
        user = request.form.to_dict()
        user['id'] = randint(1, 100)
        if len(user['nickname']) < 4:
            errors = ['Логин должен быть длиннее 4 символов!']
            return render_template('users/new.html',
                                   user=user, errors=errors), 422
        read_repo = json.loads(repo.read())
        read_repo.append(user)
        with open('repo.json', 'w') as repo:
            repo.write(json.dumps(read_repo))
    flash('Регистрация прошла успешно!', 'success')
    return redirect(url_for('get_users'), code=302)


@app.route('/users/<int:id>/update', methods=['GET', 'POST'])
def user_update(id):
    with open('repo.json', 'r') as repo:
        read_repo = json.loads(repo.read())
        for user in read_repo:
            if user['id'] == id:
                errors = []
                
                if request.method == 'GET':
                    return render_template('users/edit.html',
                                           errors=errors, user=user)
                
                if request.method == 'POST':
                    data = request.form.to_dict()
                    errors = validate(data)
                    if errors:
                        return render_template('users/edit.html',
                                               errors=errors, user=user)
                    user['nickname'] = data['nickname']
                    user['email'] = data['email']
                    with open('repo.json', 'w') as repo:
                        repo.write(json.dumps(read_repo))
    flash('Обновлено!', 'success')
    return redirect(url_for('get_users'))


@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    with open('repo.json', 'r') as repo:
        read_repo = json.loads(repo.read())
        for index, user in enumerate(read_repo):
            if user['id'] == id:
                user_name = user['nickname']
                read_repo.pop(index)
                with open('repo.json', 'w') as repo:
                    repo.write(json.dumps(read_repo))
    flash(f'Пользователь {user_name} был удален!', 'success')
    return redirect(url_for('get_users'))

def validate(user):
    errors = {}
    if user['nickname'] == '':
        errors['nickname'] = "Can't be blank"
    if user['email'] == '':
        errors['email'] = "Can't be blank"
    return errors


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        user_login = request.form['email']
        session['user'] = user_login
        return redirect(url_for('get_users'))
    
    if request.method == 'GET':
        email = ''
        return render_template('users/login.html', email=email)
    
    
@app.route('/logout', methods=['POST'])
def user_logout():
    session.clear()
    return redirect(url_for('user_login'))
    