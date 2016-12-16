import webapp2

import models
import utils

from google.appengine.ext import db

class BlogHandler(utils.Handler):
    """This handler is responsible to list blog posts.

    It gets the latest 10 blog posts and renders. Only when a user is logged-in,
    the blog is avalible to read.
    """
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 10;")
        self.render_with_valid_user('blog.html', blogs=blogs)

class NewPostHandler(utils.Handler):
    """This handler is responsible to show a new post form and create a new post.

    When a user is logged-in, the new psot form will show up. The new post will be
    created with both subject and content.
    """
    def render_newpost(self, subject="", content="", error=""):
        self.render_with_valid_user('newpost.html', title="New Post",
                                    subject=subject, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        user = self.get_user()

        if user and subject and content:
            blog = models.Blog(author=user, subject=subject, content=content)
            blog.put()
            # getkey
            path = '/blog/%s' % blog.key().id()
            self.redirect(path) # with key, permlink
        else:
            error = "we need both a subject and some content!"
            self.render_newpost(subject, content, error)

class DeletePostHandler(utils.Handler):
    """This Handler is responsible for deleting a post.

    The deletion has two steps, first click Delete button followed by clicking Confirm Delete
    button.
    """
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
    """This handler is responsible for editing a blog post.

    Only when a logged-in user is an author of the post, an edit form shows up.
    The user has a choice to cancel. The user updated content or subject, and clicks
    Submit button, the post will be updated.
    """
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
    """This handler is responsible for a couple of features tied to the blog post shown.

    1. Shows only one post with title, content, user name, number of likes so far
    2. Has a like button to upvote
    3. Shows comments if there's any
    4. Shows a form to add a comment
    5. If the author of comments are the current logged-in user, delete/edit comments buttons
       are show up.
    """
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
    """This handler is responsible for counting up upvotes (a.k.a likes)

    If a current user is not the author of the post, the user can upvote(or like)
    the post.
    """
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
