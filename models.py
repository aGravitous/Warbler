"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class FollowersFollowee(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'follows'

    followee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    likes = db.relationship('Like', backref='user')

    messages = db.relationship('Message', backref='user')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(FollowersFollowee.follower_id == id),
        secondaryjoin=(FollowersFollowee.followee_id == id),
        backref="following")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if
                           user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_user`?"""

        found_user_list = [user for user in self.following
                           if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    likes = db.relationship('Like', backref='message')

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False,
    )

    def __repr__(self):
        return f"""<Message #{self.id}: {self.text},
        {self.timestamp}, {self.user_id}>"""

    def is_liked_by(self, curr_user):
        """Is a message liked by `user`?"""

        liked_list = [like for like in self.likes if
                      like.user_id == curr_user.id]
        return len(liked_list) == 1


class Like(db.Model):
    """ An individual 'like'. """

    __tablename__ = "likes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False,
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete="cascade"),
        nullable=False,
    )

    def __repr__(self):
        return f"<Like #{self.id}: {self.user_id}, {self.message_id}>"


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
