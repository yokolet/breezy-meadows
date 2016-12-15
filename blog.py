import webapp2

import models
import utils

from google.appengine.ext import db

class BlogHandler(utils.Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 10;")
        self.render_with_valid_user('blog.html', blogs=blogs)

class NewPostHandler(utils.Handler):
    def render_newpost(self, subject="", content="", error=""):
        self.render_with_valid_user('newpost.html', subject=subject, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            b = models.Blog(subject=subject, content=content)
            b.put()
            # getkey
            path = '/blog/%s' % b.key().id()
            self.redirect(path) # with key, permlink
        else:
            error = "we need both a subject and some content!"
            self.render_newpost(subject, content, error)

class SinglePostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        self.render_with_valid_user('single_post.html', blog=blog)

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               (r'/blog/(\d+)', SinglePostHandler)],
                              debug=True)
