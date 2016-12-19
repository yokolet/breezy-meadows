import utils
import webapp2


class MainPage(utils.Handler):
    """This handler is responsible to show top page.

    It shows simple login or signup page.
    """
    def get(self):
        self.render("index.html")

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
