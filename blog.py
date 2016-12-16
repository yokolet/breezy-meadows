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
        self.render_with_valid_user('newpost.html', title="New Post",
                                    subject=subject, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            user = self.get_user()
            blog = models.Blog(author=user, subject=subject, content=content)
            blog.put()
            # getkey
            path = '/blog/%s' % blog.key().id()
            self.redirect(path) # with key, permlink
        else:
            error = "we need both a subject and some content!"
            self.render_newpost(subject, content, error)

class DeletePostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        if blog and (blog.author.key().id() == self.get_user().key().id()):
            self.render('single_post.html', op="delete-confirm", blog=blog)
        else:
            self.redirect('/blog')

class EditPostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        if blog and (blog.author.key().id() == self.get_user().key().id()):
            self.render('newpost.html', title='Edit Post',
                        subject=blog.subject, content=blog.content)
        else:
            self.redirect('/blog')

    def post(self, ident):
        op = self.request.get('submit')
        path = '/blog/%s' % ident
        if op == 'Cancel':
            self.redirect(path)
        else:
            blog = models.Blog.get_by_id(long(ident))
            if blog and (blog.author.key().id() == self.get_user().key().id()):
                subject = self.request.get('subject')
                content = self.request.get('content')
                if subject and content:
                    blog.subject = subject
                    blog.content = content
                    blog.put()
                    self.redirect(path) # with key, permlink
                else:
                    error = "we need both a subject and some content!"
                    self.render('newpost.html', title='Edit Post',
                                subject=subject, content=content, error=error)
            else:
                self.redirect('/blog')

class SinglePostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        self.render_with_valid_user('single_post.html', blog=blog)

    def post(self, ident):
        op = self.request.get('submit')
        print(ident)
        print(op)
        if op == 'Edit':
            path = '/blog/editpost/%s' % ident
            self.redirect(path)
        elif op == 'Delete':
            self.redirect('/blog/deletepost/%s' % ident)

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               (r'/blog/editpost/(\d+)', EditPostHandler),
                               (r'/blog/deletepost/(\d+)', DeletePostHandler),
                               (r'/blog/(\d+)', SinglePostHandler)],
                              debug=True)
