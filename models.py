import hashlib
import random
import string

from google.appengine.ext import db

### Model
def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for _ in xrange(length))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def validate_pw(name, pw, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, pw, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, username):
        user = User.all().filter('username = ', username).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        pw_hash = make_pw_hash(username, password)
        if email:
            return User(parent = users_key(),
                        username = username,
                        pw_hash = pw_hash,
                        email = email)
        else:
            return User(parent = users_key(),
                        username = username,
                        pw_hash = pw_hash)

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
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
