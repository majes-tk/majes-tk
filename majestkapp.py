# SimpleOrder main app file


# Handle Imports
from sqlite3 import IntegrityError
from flask import Flask, session, render_template, redirect, url_for, request, abort, g
from flask_migrate import Migrate
import sqlalchemy
import models as m

try:
    import userconfig as config
except:
    import config


import json
import user
import git
import os
import time
import datetime

# prepare language files

with open("lang/"+config.LANGUAGE+".json", 'r', encoding="utf-8") as langfile:
    lang = json.load(langfile)

# get current git commit shortname to display in the about page

version = "0.7"

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simpleorder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
m.db.init_app(app)
Migrate(app, m.db, render_as_batch=True)


@app.before_request
def initializeRequest():
    # make some variables available to the main script
    g.current_user = None
    if "login" in session.keys() and session['login']:
        g.current_user = user.get_user(session['acc_id'])


@app.context_processor
def global_template_vars():
    # make some variables available to the templating engine
    return {
        "sitename": config.SITE_NAME,
        "lang": lang,
        "stversion": version,
        "current_user": g.current_user,
        "ctime": time.ctime,
        "getTime": user.getTime,
        "hasValidReply": user.hasValidReply
    }


@app.errorhandler(404)
def pageNotFound(e):
    # set a custom 404 error page to make the web app pretty
    return render_template('404error.html'), 404


@app.errorhandler(403)
def accessDenied(e):
    # set a custom 403 error page to make the web app pretty
    return render_template('403error.html'), 403


@app.errorhandler(500)
def serverError(e):
    # set a custom 500 error page to make the web app pretty
    return render_template('500error.html'), 500


@app.route('/')
def home():
    # the index and home landing page. this displays all the active and closed orders.
    if config.REQUIRE_LOGIN:
        if "login" in session.keys() and session['login']:
            return render_template('index.html', orders=m.Order.query.all())
        else:
            return redirect(url_for("login"))
    else:
        return render_template("index.html")


@app.route('/create', methods=['GET', 'POST'])
def createOrder():
    # the page to create a new order on.
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            user.create_order(
                request.form["order-title"], request.form["order-text"], None, g.current_user, None)
            return redirect(url_for('home'))
        return render_template('order-create.html')
    else:
        abort(403)

# the page to view and edit orders.


@app.route('/view-order/<orderid>', methods=['GET', 'POST'])
def viewOrder(orderid):
    order = m.Order.query.filter_by(id=orderid).first()
    if order == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            order.assigned_to_id = request.form["new-assignee-id"]
            m.db.session.commit()
        order_replies = m.OrderReply.query.filter_by(main_order=order)
        return render_template('order-view.html', order=order, replies=order_replies)
    else:
        abort(403)


@app.route('/view-order/<orderid>/close')
def closeOrder(orderid):
    order = m.Order.query.filter_by(id=orderid).first()
    if order == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == order.created_by_id or g.current_user.highPermissionLevel:
            order.is_open = False
            m.db.session.commit()
            return redirect(url_for('viewOrder', orderid=orderid))
        else:
            abort(403)
    else:
        abort(403)


@app.route('/view-order/<orderid>/reopen')
def reopenOrder(orderid):
    order = m.Order.query.filter_by(id=orderid).first()
    if order == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == order.created_by_id or g.current_user.highPermissionLevel:
            order.is_open = True
            m.db.session.commit()
            return redirect(url_for('viewOrder', orderid=orderid))
        else:
            abort(403)
    else:
        abort(403)


@app.route('/view-order/<orderid>/hide')
def hideOrder(orderid):
    order = m.Order.query.filter_by(id=orderid).first()
    if order == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.highPermissionLevel:
            order.hidden = True
            m.db.session.commit()
            return redirect(url_for('viewOrder', orderid=orderid))
        else:
            abort(403)
    else:
        abort(403)


@app.route('/view-order/<orderid>/unhide')
def unhideOrder(orderid):
    order = m.Order.query.filter_by(id=orderid).first()
    if order == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.highPermissionLevel:
            order.hidden = False
            m.db.session.commit()
            return redirect(url_for('viewOrder', orderid=orderid))
        else:
            abort(403)
    else:
        abort(403)


@app.route('/view-order/<orderid>/reply', methods=['POST'])
def createOrderReply(orderid):
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            if request.form.get('action') == "SaveNote":
                user.create_order_reply(
                    request.form["reply-text"], None, g.current_user, orderid, isNote=True)
            else:
                user.create_order_reply(
                    request.form["reply-text"], None, g.current_user, orderid)
            return redirect(url_for('viewOrder', orderid=orderid))
        return redirect(url_for('viewOrder', orderid=orderid))
    else:
        abort(403)


# the about page. this shows the current software version and some general information about SimpleOrder.
@app.route('/about')
def about():
    return render_template('about.html')

# the login page. this allows a user to authenticate to enable them to create and edit orders.


@app.route('/login', methods=['GET', 'POST'])
def login(message=None):
    if request.method == 'POST':
        # make sure the login string is only in lowercase
        username = str.lower(request.form["login"])
        password = request.form["password"]
        acc = user.verify_login(username, password)
        if acc:
            session['login'] = True
            session['acc_id'] = acc.id
            return redirect(url_for('home'))
        else:
            message = lang["login-error"]
    return render_template('user-login.html', message=message)

# provide a logout url. we dont want users to get stuck logged in :)


@app.route('/logout')
def logout():
    session['login'] = False
    session['acc_id'] = None
    return redirect(url_for('home'))

# the password reset page to enable the users to reset their own password, provided they know their own email address.


@app.route('/pwreset', methods=['GET', 'POST'])
def resetPW():
    message = None
    if request.method == 'POST':
        message = lang['password-reset-form-message']
        userobj = m.User.query.filter_by(email=request.form["email"]).first()
        if userobj == None:
            message = lang['user-not-found-error']
            return render_template('user-password-reset.html', message=message)
        user.resetpw(userobj)
        return render_template('user-password-reset.html', message=message)
    return render_template('user-password-reset.html', message=message)


@app.route('/add-admin', methods=['GET', 'POST'])
def addAdmin():
    
    if os.path.exists(config.CREATE_ADMIN_FILE):
        try:
            if request.method == 'POST':
                user.create_user(str.lower(request.form["username"]), request.form["email"], user.hashPassword(
                    request.form["password"]), highPermissionLevel=True)
                return redirect(url_for('login'))
        except Exception:
            return render_template('user-signup.html', perms=lang["low-perms"], message=lang["user-create-error"])
        return render_template('user-signup.html', perms=lang["low-perms"])
    else:
        abort(403)


@app.route('/add-user', methods=['GET', 'POST'])
def addUser():
    try:
        if request.method == 'POST':
            user.create_user(
                str.lower(request.form["username"]), 
                request.form["email"], 
                user.hashPassword(
                request.form["password"]), 
                highPermissionLevel=False)
            return redirect(url_for('login'))
    except Exception:
        return render_template('user-signup.html', perms=lang["low-perms"], message=lang["user-create-error"])
    return render_template('user-signup.html', perms=lang["low-perms"])


@app.route('/add-dish/<restaurantid>', methods=['GET', 'POST'])
def addDish(restaurantid):
    if (
        "login" in session.keys() 
        and session['login'] 
        and ( 
            g.current_user.highPermissionLevel 
            or g.current_user.isRestaurant
            )
        ):
        if request.method == 'POST':
            user.create_dish(
                request.form['dishname'],
                float(request.form['price']),
                request.form['description'],
                m.Restaurant.query.filter_by(id=restaurantid).first().id
            )
            return redirect(url_for('home'))
        return render_template('dish-create.html')
    else: 
        abort(403)

@app.route('/add-restaurant', methods=['GET', 'POST'])
def addReastaurant():
    if g.current_user.highPermissionLevel:
        if request.method == 'POST':
            id = user.create_restaurant(
                request.form["restaurant-name"],
                request.form["restaurant-info"],
                request.form["restaurant-style"],
                request.form["restaurant-delivery_cost"], 
                request.form["linked-user-email"])
            print(id)
            return redirect(url_for('home'))
        return render_template('restaurant-create.html')
    abort

@app.route('/view-restaurant/<restaurantid>')
def view_restaurant(restaurantid):
    if "login" in session.keys() and session["login"]:
        restaurant = m.Restaurant.query.filter_by(id=restaurantid).first()
        if restaurant == None:
            abort(404)
        if g.current_user.isRestaurant: 
            orders = m.Order.query.filter_by(restaurant_id = restaurantid)
        dishesquery = m.Dish.query.filter_by(served_at_id = restaurantid)
        dishes = []
        for i in range(len(list(dishesquery))):
            dish = dishesquery[i]
            print(dish.media)
            dish.media = json.loads(dish.media)
            dishes.append(dish)
        return render_template('restaurant-view.html', orders=orders, dishes=dishes, restaurant=restaurant)
    else:
        abort(403)


@app.route('/account-settings', methods=['GET', 'POST'])
def changeSettings():
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            try:
                user.modify_user_password(
                    g.current_user.id, user.hashPassword(request.form["password"]))
            except sqlalchemy.exc.IntegrityError:
                return render_template('account-settings.html', message=lang["user-modify-error"])
            return redirect(url_for('home'))
        return render_template('account-settings.html')
    else:
        abort(403)


@app.route('/admin-settings', methods=['GET', 'POST'])
def adminUserSettigs():
    if "login" in session.keys() and session['login'] and g.current_user.highPermissionLevel:
        if request.method == 'POST':
            try:
                user.modify_user_password(user.get_userid(
                    request.form["username"]), user.hashPassword(request.form["password"]))
            except sqlalchemy.exc.IntegrityError:
                return render_template('admin-settings.html', message=lang["user-modify-error"])
            return redirect(url_for('home'))
        return render_template('admin-settings.html')
    else:
        abort(403)
