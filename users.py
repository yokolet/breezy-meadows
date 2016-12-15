import re
import webapp2

import models
import utils

### Controler and View
patterns = {'username': re.compile(r'^[a-zA-Z0-9_-]{3,20}$'),
            'password': re.compile(r'^.{3,20}$'),
            'email': re.compile(r'^[\S]+@[\S]+.[\S]+$')}

def validate_thing(key, value):
    return value and patterns[key].match(value)

error_messages = {'username': "That's not a valid username.",
                  'password': "That wasn't a valid password.",
                  'verify': "Your password didn't match.",
                  'email': "That's not a valid email."}

class SignupHandler(utils.Handler):
    def get(self):
        self.render("signup.html", errors={}, values={})

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        have_error = False
        errors = {}

        if not validate_thing('username', username):
            have_error = True
            errors['username'] = error_messages['username']

        if not validate_thing('password', password):
            have_error = True
            errors['password'] = error_messages['password']
        elif password != verify:
            have_error = True
            errors['verify'] = error_messages['verify']

        if email:
            if not validate_thing('email', email):
                have_error = True
                errors['email'] = error_messages['email']
            
        values = dict(username = username,
                      password = password,
                      verify = verify,
                      email = email)

        if have_error:
            self.render("signup.html", errors = errors, values = values)
        else:
            self.register(values)

    def register(self, values):
        user = models.User.by_name(values['username'])
        if user:
            errors = dict(username = 'That user already exists.')
            self.render("signup.html", errors = errors, values = values)
        else:
            user = models.User.register(values['username'], values['password'], values['email'])
            user.put()
            self.set_secure_cookie('user_id', str(user.key().id()))
            self.redirect('/welcome')

class WelcomeHandler(utils.Handler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        if user_id:
            user = models.User.by_id(int(user_id))
            if user:
                self.render("welcome.html", username = user.username)
            else:
                self.redirect('/signup')
        else:
            self.redirect('/signup')

class LoginHandler(utils.Handler):
    def get(self):
        self.render('login.html', errors = {}, values = {})

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = models.User.login(username, password)
        if user:
            self.set_secure_cookie('user_id', str(user.key().id()))
            self.redirect('/welcome')
        else:
            error = 'Invalid login'
            values = dict(username = username, password = password)
            self.render('login.html', error = error, values = values)
        
class LogoutHandler(utils.Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/')

app = webapp2.WSGIApplication([('/signup', SignupHandler),
                               ('/welcome', WelcomeHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler)],
                              debug=True)
