from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(400), unique=True, nullable=False)
    fullname = db.Column(db.Text, unique=False, nullable=True)
    email = db.Column(db.String(400), unique=True, nullable=False)
    password = db.Column(db.String(1000), unique=False, nullable=True)
    passwordToken = db.Column(db.Text, unique=False, nullable=True)
    passwordResetTimer = db.Column(
        db.Integer, unique=False, nullable=True, default=-1)
    highPermissionLevel = db.Column(
        db.Boolean, unique=False, nullable=False, default=False)
    isRestaurant = db.Column(
        db.Boolean, unique=False, default=False)

    def __repr__(self):
        return '<User %r, %s, %s>' % self.username, self.email, self.isRestaurant


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_open = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    time = db.Column(db.Integer, unique=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hidden = db.Column(db.Boolean, unique=False, default=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))

    restaurant = db.relationship(
        "Restaurant", backref="orders_at", foreign_keys=[restaurant_id])

    created_by = db.relationship(
        'User', backref='orders_created_by', foreign_keys=[created_by_id])

    def __repr__(self):
        return '<Order %s: %r>' % (self.id, self.title)


class OrderReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, unique=False, nullable=False)
    media = db.Column(db.Text, unique=False, nullable=True)
    isNote = db.Column(db.Boolean, unique=False, nullable=True)
    time = db.Column(db.Integer, unique=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    main_order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    created_by = db.relationship(
        'User', backref='order_reply_by', foreign_keys=[created_by_id])
    main_order = db.relationship(
        'Order', backref='order_reply_main_order', foreign_keys=[main_order_id])

    def __repr__(self):
        return '<OrderReply to %s>' % self.main_order


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    media = db.Column(db.Text, unique=False, nullable=True)
    info = db.Column(db.Text, nullable=True)
    style = db.Column(db.Text, nullable=False)
    show_tally = db.Column(db.Boolean, default=False)
    tally_amount = db.Column(db.Integer, default=0, nullable=False)
    delivery_cost = db.Column(db.Integer, default=0, nullable=True)
    linked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=0, nullable=False)
    linked_user = db.relationship(
        'User', backref='restaurant_of', foreign_keys=[linked_user_id])
    
    def __repr__(self):
        return "<Restaurant %s of user %s>" % (self.name, self.linked_user.name)


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    names_internationalized = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, default=0, nullable=False)
    info = db.Column(db.Text, nullable=False)
    media = db.Column(db.Text, nullable=True)
    served_at_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)

    served_at = db.relationship(
        "Restaurant", backref="has_dishes", foreign_keys=[served_at_id])

    def __repr__(self):
        return "<Dish %s, by %s>" % (self.name, self.served_at)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_note = db.Column(db.Text, nullable=True)
    user = db.relationship(
        'User', backref="Cart_of", foreign_keys=[user_id])
    dish = db.relationship(
        'Dish', backref="Cart_with", foreign_keys=[dish_id])

    def __repr__(self):
        return "<CartItem %s in user cart by %s" % (self.dish, self.user)
