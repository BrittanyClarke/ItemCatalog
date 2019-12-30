#!/usr/bin/pythonA
# -*- coding: utf-8 -*-
from decimal import Decimal
from flask import session as login_session
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import json
from flask import Flask, render_template, request, url_for, redirect, \
    jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'
                                                                ]['client_id']
APPLICATION_NAME = 'Catalog Application'

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# User Information
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print("CREATED NEW USER!!!")
    print(user.id)
    return user.id

def getUserInfo(user_id):
    user_id = user_id
    print(user_id)
    print("ABOVE THIS ^" )
    user = session.query(User).filter_by(id=user_id) #.one()    
    print(user)
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        print(user.id)
        return user.id
    except:
        return None

# Create login route

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Login functionality

@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("INSIDE GCONNECT")
    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = \
            make_response(json.dumps('Failed to upgrade' +
                                     'the authorization code.'
                                     ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID" +
                                 "doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token's client ID" + 
                                     "does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is' +
                          'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id #('%.11e' % Decimal(gplus_id))

    print("BELOW THIS: ")
    print(login_session['gplus_id'])
    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    '''
    # see if user exists, if it doesn't make a new one
    user_id = getUserInfo(login_session['gplus_id'])
    print("USERID:")
    print(user_id)
    print("GPLUSID")
    print(login_session['gplus_id'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    '''
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    flash('you are now logged in as %s' % login_session['username'])
    
    return output


# Logout functionality

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully' + 
                                            'disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategory'))
    else:
        response = \
            make_response(json.dumps('Failed to revoke token' + 
                                     'for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Create route for homepage for all categories & items

@app.route('/')
@app.route('/catalog/')
def showCategory():

    # items = session.query(CategoryItem).all()
    # categories = session.query(Category).all()
    # category = session.query(Category).filter_by(name=category_name).one()
    # items = session.query(CategoryItem).all()

    items = \
        session.query(CategoryItem).order_by(
                                            CategoryItem.creation_date.desc()
                                            ).limit(5).all()
    categories = session.query(Category).all()
    return render_template('categories.html', items=items,
                           categories=categories)


# Create route for specific category with items

@app.route('/catalog/<category_name>/items/')
@app.route('/catalog/<category_name>/')
def showCategory1(category_name):
    category = \
        session.query(Category).filter_by(name=category_name).one()
    items = \
        session.query(CategoryItem).filter_by(category_id=category.id).all()
    categories = session.query(Category).all()
    return render_template('catalog.html', items=items,
                           category=category, categories=categories)


# Create route for JSON endpoint

@app.route('/catalog.json')
def catalogJson():
    categories = session.query(Category).all()
    catalog = []

    for category in categories:
        items = \
            session.query(CategoryItem).filter_by(category_id=category.id)
        category = category.serialize
        category['Item'] = [item.serialize for item in items]
        catalog.append(category)

    return jsonify(Category=catalog)


# Create route for JSON endpoint items

@app.route('/catalog/<category_name>/<item_name>.json')
def itemJson(category_name, item_name):
    category = \
        session.query(Category).filter_by(name=category_name).one()
    item = \
        session.query(CategoryItem).filter_by(
                                              category_id=category.id,
                                              name=item_name
                                             ).one()
    result = {}
    result['CategoryItem'] = item.serialize
    return jsonify(result)


# Create route for newCategoryItem function here

@app.route('/catalog/newCategory', methods=['GET', 'POST'])
def newCategory():

    # categories = session.query(Category).all()
    # print("IN NEW ITEM FUNCTION!!!!!!!!!!")

    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name']),
        
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('newCategory.html')


# Create route for newCategoryItem function here

@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategoryItem():
    categories = session.query(Category).all()
    #category = session.query(Category).filter_by(name=category_name).one()
    #user_id=category.user_id
    
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        #user_id=login_session.get('user_id')
        #creator=getUserInfo(user_id)
        newItem = CategoryItem(name=request.form['name'],
                               category=session.query(Category).filter_by(
                                   name=request.form['category'
                                                     ]).one(),
                               user_id=login_session['gplus_id'],
                               description=request.form['description'],
                               creation_date=datetime.datetime.now())

        #user_id=category.user_id,
        print("USER: " + login_session['gplus_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('newCategoryItem.html',
                               categories=categories)


# Create route for item description

@app.route('/catalog/<category_name>/<item_name>/')
def showItemDesc(category_name, item_name):
    category = \
        session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(name=item_name,
                                                 category_id=category.id
                                                 ).one()
    creator=item.user_id
    
    if 'username' in login_session:
        print("in login sess")
        gplusID = float(login_session['gplus_id'])
        if(creator == gplusID):
            print("Works.")    
        else:
            print("doesn't work")
        return render_template('itemDesc.html', item=item, creator=creator, gplusID=gplusID)
    else:    
        return render_template('itemDesc.html', item=item)

# Create route for edit item

@app.route('/catalog/<category_name>/<item_name>/edit', methods=['GET',
           'POST'])
def editCategoryItem(category_name, item_name):
    category = \
        session.query(Category).filter_by(name=category_name).one()
    editedItem = session.query(CategoryItem).filter_by(name=item_name,
                                                       category_id=category.id
                                                       ).one()
    creator=editedItem.user_id
    
    if 'username' in login_session:
        gplusID = float(login_session['gplus_id'])

    if 'username' not in login_session or creator != gplusID:
        return redirect('/login')
            
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category = \
                session.query(Category).filter_by(name=request.form['category'
                                                                    ]).one()
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showCategory1',
                        category_name=category.name))
    else:
        categories = session.query(Category).all()
        return render_template('editcategoryitem.html',
                               item=editedItem, categories=categories)


# Create route for delete item

@app.route('/catalog/<category_name>/<item_name>/delete',
           methods=['GET', 'POST'])
def deleteCategoryItem(category_name, item_name):
    category = \
        session.query(Category).filter_by(name=category_name).one()
    itemToDelete = \
        session.query(CategoryItem).filter_by(name=item_name).one()
    creator=itemToDelete.user_id

    if 'username' in login_session:
        gplusID = float(login_session['gplus_id'])

    if 'username' not in login_session or creator != gplusID:
        return redirect('/login')
    
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory1',
                        category_name=category.name))
    else:
        return render_template('deletecategoryitem.html',
                               item=itemToDelete)

# Main method for app

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
