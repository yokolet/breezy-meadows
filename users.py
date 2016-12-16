import re
import webapp2

import models
import utils

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
    """This handler is resonsible to manage a signup.

    The handler shows a signup form. When parameters are posted,
    it checks the parameters. If there's no error or conflict,
    a new user will be created and redirect to a welcome page.
    """
    def get(self):
        self.render("signup.html", on_signup="on_singup", errors={}, values={})

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
            self.render("signup.html", on_signup="on_singup", errors = errors, values = values)
        else:
            self.register(values)

    def register(self, values):
        user = models.User.by_name(values['username'])
        if user:
            errors = dict(username = 'That user already exists.')
            self.render("signup.html", on_signup="on_signup", errors = errors, values = values)
        else:
            user = models.User.register(values['username'], values['password'], values['email'])
            user.put()
            self.set_secure_cookie('user_id', str(user.key().id()))
            self.redirect('/welcome')

class WelcomeHandler(utils.Handler):
    """This handler is responsible to show welcome page.

    When a user succesfully logged-in or signup-ed, this page will show up.
    """
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
    """This handler is responsible to allow users to log in.

    When a user is already logged-in, the page will be redirected to the welcome page.
    Otherwise, it shows a login form. Parameters in the input fields are validated.
    If the input parameters are matched to a redigered user, the welcome pages will show up.
    If there's an error, the error message appears.
    """
    def get(self):
        user = self.get_user()
        if user:
            self.redirect('/welcome')
        else:
            self.render('login.html', on_login="on_login", errors = {}, values = {})

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
            self.render('login.html', on_login="on_login", error = error, values = values)
        
class LogoutHandler(utils.Handler):
    """This handler is responsible to logout a user."""
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/')

app = webapp2.WSGIApplication([('/signup', SignupHandler),
                               ('/welcome', WelcomeHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler)],
                              debug=True)
