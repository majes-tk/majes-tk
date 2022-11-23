from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(400), unique=True, nullable=False)
    fullname = db.Column(db.Text, unique=False, nullable=True)
    email = db.Column(db.String(400), unique=True, nullable=True)
    password = db.Column(db.String(1000), unique=False, nullable=True)
    passwordToken = db.Column(db.Text, unique=False, nullable=True)
    passwordResetTimer = db.Column(
        db.Integer, unique=False, nullable=True, default=-1)
    isRestaurant = db.Column(
        db.Boolean, unique=False, nullable=True, default=False)
    highPermissionLevel = db.Column(
        db.Boolean, unique=False, nullable=False, default=False)

    def __repr__(self):
        return '<User %r, %s, %s>' % self.username, self.email, self.isRestaurant


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), unique=False, nullable=True)
    is_open = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    text = db.Column(db.Text, unique=False, nullable=False)
    # This contains base64'ed binary images and videos in a python list.
    media = db.Column(db.Text, unique=False, nullable=True)
    # The time the ticket was created in epoch seconds
    time = db.Column(db.Integer, unique=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hidden = db.Column(db.Boolean, unique=False, default=False)

    created_by = db.relationship(
        'User', backref='tickets_created_by', foreign_keys=[created_by_id])

    def __repr__(self):
        return '<Ticket %s: %r>' % (self.id, self.title)


class TicketReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, unique=False, nullable=False)
    media = db.Column(db.Text, unique=False, nullable=True)
    isNote = db.Column(db.Boolean, unique=False, nullable=True)
    # The time the ticket reply was created in epoch seconds
    time = db.Column(db.Integer, unique=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    main_ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

    created_by = db.relationship(
        'User', backref='ticket_reply_by', foreign_keys=[created_by_id])
    main_ticket = db.relationship(
        'Ticket', backref='ticket_reply_main_ticket', foreign_keys=[main_ticket_id])

    def __repr__(self):
        return '<TicketReply to %s>' % self.main_ticket
