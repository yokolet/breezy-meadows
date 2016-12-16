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
            self.render_with_valid_user('single_post.html', op='delete-confirm', blog=blog)
        else:
            self.redirect('/blog')

    def post(self, ident):
        op = self.request.get('submit')
        if op == 'Confirm Delete':
            blog = models.Blog.get_by_id(long(ident))
            if blog and (blog.author.key().id() == self.get_user().key().id()):
                blog.delete()
        self.redirect('/blog')

class EditPostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        if blog and (blog.author.key().id() == self.get_user().key().id()):
            self.render('newpost.html', title='Edit Post', username=self.get_user(),
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
            user = self.get_user()
            if blog and (blog.author.key().id() == user.key().id()):
                subject = self.request.get('subject')
                content = self.request.get('content')
                if subject and content:
                    blog.subject = subject
                    blog.content = content
                    blog.put()
                    self.redirect(path) # with key, permlink
                else:
                    error = "we need both a subject and some content!"
                    self.render('newpost.html', title='Edit Post', username=user.username,
                                subject=subject, content=content, error=error)
            else:
                self.redirect('/blog')

class SinglePostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        post_comments = sorted(blog.comments, key=lambda x: x.created)
        self.render_with_valid_user('single_post.html', blog=blog, post_comments=post_comments)

    def post(self, ident):
        op = self.request.get('submit')
        print(op)
        if op == 'Edit':
            self.redirect('/blog/editpost/%s' % ident)
        elif op == 'Delete':
            self.redirect('/blog/deletepost/%s' % ident)
        elif op == 'Add':
            blog = models.Blog.get_by_id(long(ident))
            user = self.get_user()
            print(blog)
            print(user)
            if blog and user:
                comment_content = self.request.get('comment')
                comment = models.Comment(author=user, blog=blog, content=comment_content)
                comment.put()
            self.redirect('/blog/%s' % ident)
        elif op == 'Update':
            blog = models.Blog.get_by_id(long(ident))
            user = self.get_user()
            if blog and user:
                comment_id = self.request.get('comment_id')
                comment = models.Comment.get_by_id(long(comment_id))
                comment_content = self.request.get('comment')
                if comment:
                    comment.content = comment_content
                    comment.put()
            self.redirect('/blog/%s' % ident)
        elif op == 'Delete Comment':
            comment_id = self.request.get('comment_id')
            comment = models.Comment.get_by_id(long(comment_id))
            if comment.author.key().id() == self.get_user().key().id():
                comment.delete()
            self.redirect('/blog/%s' % ident)
        elif op == 'Edit Comment':
            comment_id = self.request.get('comment_id')
            comment = models.Comment.get_by_id(long(comment_id))
            print(comment_id)
            print(comment.content)
            print(comment.author)
            print(self.get_user())
            if comment and (comment.author.key().id() == self.get_user().key().id()):
                blog = models.Blog.get_by_id(long(ident))
                post_comments = sorted(blog.comments, key=lambda x: x.created)
                print(post_comments)
                self.render('single_post.html', blog=blog, username=self.get_user().username,
                            post_comments=post_comments, edit_comment=comment)
        else:
            self.redirect('/blog/%s' % ident)

class UpvotePostHandler(utils.Handler):
    def get(self, ident):
        blog = models.Blog.get_by_id(long(ident))
        if blog and (blog.author.key().id() != self.get_user().key().id()):
            blog.upvotes = blog.upvotes + 1
            blog.put()
        self.redirect('/blog/%s' % ident)

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               (r'/blog/editpost/(\d+)', EditPostHandler),
                               (r'/blog/deletepost/(\d+)', DeletePostHandler),
                               (r'/blog/upvote/(\d+)', UpvotePostHandler),
                               (r'/blog/(\d+)', SinglePostHandler)],
                              debug=True)
