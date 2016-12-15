import utils
import webapp2

class MainPage(utils.Handler):
    def get(self):
        self.render("index.html")

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
