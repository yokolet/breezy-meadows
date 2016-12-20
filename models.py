import hashlib
import random
import string

from google.appengine.ext import db


# Model
def make_salt(length=5):
    """A function to create a salt of given lenght, 5 by default"""
    return ''.join(random.choice(string.letters) for _ in xrange(length))


def make_pw_hash(name, pw, salt=None):
    """A fucntion to create a password hash with a salt.

    The salt may or may not be given. If no salt given,
    this function creates it.
    """
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def validate_pw(name, pw, h):
    """A function to validate password against saved hash. """
    salt = h.split(',')[0]
    return h == make_pw_hash(name, pw, salt)


def users_key(group='default'):
    """A function to get users' key"""
    return db.Key.from_path('users', group)


class User(db.Model):
    """User model class

    Each user has username, password hash, email, and the datetime this user
    was created. By reference, each User will have comment_set.
    """
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, username):
        user = User.all().filter('username = ', username).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        pw_hash = make_pw_hash(username, password)
        if email:
            return User(parent=users_key(),
                        username=username,
                        pw_hash=pw_hash,
                        email=email)
        else:
            return User(parent=users_key(),
                        username=username,
                        pw_hash=pw_hash)

    @classmethod
    def validate_user(cls, name, pw):
        user = cls.by_name(name)
        if user and validate_pw(name, pw, user.pw_hash):
            return user

    @classmethod
    def login(cls, username, pw):
        user = cls.by_name(username)
        if user and validate_pw(username, pw, user.pw_hash):
            return user


class Blog(db.Model):
    """Blog model class.

    Blog has attributes:
        author: reference to a user who wrote a blog
        subject: string, a subjet of a blog
        content: text, a content of a blog
        upvotes: integer, a total number of voted (liked)
        voted_users: list of long, a list of user ids who voted
        created: datetime, the time a blog was created
    By reference, each Blog instance will have multiple comments."
    """
    author = db.ReferenceProperty(User, required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    upvotes = db.IntegerProperty(default=0L)
    voted_users = db.ListProperty(long)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


class Comment(db.Model):
    """Comment model class.

    Comment has a reference to an author and blog, content, created datetime.
    """
    author = db.ReferenceProperty(User, required=True)
    blog = db.ReferenceProperty(Blog, required=True,
                                collection_name='comments')
    content = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
