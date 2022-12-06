import bcrypt
import smtpconfig
import json
import time
import datetime
import random
import string
from majestkapp import m
import base64

import config

# prepare language files

with open("lang/"+config.LANGUAGE+".json",'r',encoding="utf-8") as langfile:
    lang = json.load(langfile)

def resetpw(user):
    newPassword = ''.join(random.choices(string.ascii_uppercase + string.digits, k = random.randint(20,30)))
    user.password = hashPassword(newPassword)
    m.db.session.commit()   
    sendmail(user.email, lang["password-reset-mail"].replace("%PW%", newPassword), lang["password-reset"]+" | "+config.SITE_NAME)
    del(newPassword)

def verify_login(u, p):
    potential_user = m.User.query.filter_by(username=u.lower()).first()
    if potential_user:
        if bcrypt.checkpw(p.encode('utf-8'), potential_user.password.encode('utf-8')):
            return potential_user

    return False

def hashPassword(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode()

def get_userid(username):
    return m.User.query.filter_by(username = username).first().id

def get_user(userid):
    return m.User.query.get(userid)

def create_order(created_by):
    new_order = m.Order() 
    new_order.created_by_id = created_by.id
    new_order.is_open = True
    new_order.time = datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
    new_order.hidden = False
    m.db.session.add(new_order)
    m.db.session.commit()
    currentCart = m.CartItem.query.filter_by(user_id = created_by.id).all()
    new_order.price = config.FEE + calcTotal(created_by.id)
    for item in currentCart:
        new_order_item = m.OrderItem()
        new_order_item.dish_id = item.dish_id
        new_order_item.item_note = item.item_note
        new_order_item.order_id = new_order.id
        m.db.session.add(new_order_item)
        new_order.price += item.dish.price
        m.CartItem.query.filter_by(id = item.id).delete() 
    m.db.session.commit()
    return new_order.id

def create_order_reply(text, media, created_by, main_order_id, isNote = False):
    new_order = m.OrderReply()
    new_order.text = text   
    new_order.media = media
    new_order.isNote = isNote
    new_order.time = time.time()
    new_order.created_by = created_by
    new_order.main_order_id = main_order_id
    m.db.session.add(new_order)
    m.db.session.commit()

def create_user(username, email, hashedPassword, passwordResetTimer = -1, highPermissionLevel = 0):
    new_user = m.User()
    new_user.username = username.lower()
    new_user.fullname = username
    new_user.email = email
    new_user.password = hashedPassword
    new_user.passwordResetTimer = passwordResetTimer
    new_user.highPermissionLevel = highPermissionLevel
    try:
        m.db.session.add(new_user)
        m.db.session.commit()
    except:
        m.db.session.rollback()
        raise ValueError('Value already in use.')

def create_dish(dishname, price=0.0, description = "", served_at_id = 0):
    new_dish = m.Dish()
    new_dish.name = dishname
    new_dish.price = float(price)
    new_dish.info = description
    new_dish.media = None
    new_dish.served_at = m.Restaurant.query.filter_by(id=served_at_id).first()
    m.db.session.add(new_dish)
    m.db.session.commit()

def create_restaurant(restaurant_name, info, style, delivery_cost, useremail):
    new_restaurant = m.Restaurant()
    new_restaurant.name = restaurant_name
    new_restaurant.info = info
    new_restaurant.style = style
    new_restaurant.delivery_cost = float(delivery_cost)
    linkedUser = m.User.query.filter_by(email=useremail).first()
    new_restaurant.linked_user = linkedUser
    m.db.session.add(new_restaurant)
    linkedUser.isRestaurant = True
    m.db.session.commit()
    return new_restaurant.id 

def add_to_cart(dishid, userid):
    new_cart_item = m.CartItem()
    new_cart_item.user_id = userid
    new_cart_item.dish_id = dishid
    m.db.session.add(new_cart_item)
    m.db.session.commit()

def remove_from_cart(dishid, userid):
    m.db.session.delete(m.CartItem.query.filter_by(dish_id = dishid, user_id = userid).first())
    m.db.session.commit()

def calcTotal(userid):
    total = 0
    for CartItem in m.CartItem.query.filter_by(user_id = userid).all():
        total += CartItem.dish.price
    return total

def modify_user_password(userid, newPasswordHash):
    modified_user = get_user(userid)
    modified_user.password = newPasswordHash
    m.db.session.commit()
    

def sendmail(address, htmlcontent, subject):
    import smtplib, ssl
    mailstring = "From: "+smtpconfig.SMTP_USER+"\nTo: "+address+"\nSubject: "+subject+"\n\n"+htmlcontent+"\n"
    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpconfig.SMTP_SERVER, smtpconfig.SMTP_PORT, context=ssl_context) as smtpserver:
        smtpserver.login(smtpconfig.SMTP_USER, smtpconfig.SMTP_PASSWORD)
        smtpserver.sendmail(smtpconfig.SMTP_USER, address, mailstring)

def getTime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime(config.TIMEFORMAT)
    except:
        return "Invalid time"

def hasValidReply(orderid):
    orderReplyList = m.OrderReply.query.filter_by(main_order_id = orderid).all()
    for reply in orderReplyList:
        if m.User.query.filter_by(id = reply.created_by_id).first().highPermissionLevel:
            return True
    return False