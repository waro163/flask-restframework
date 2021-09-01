class BaseMiddleware(object):

    def __init__(self, app):
        self.app = app
        self.register_handlers()
    
    def register_handlers(self):
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

    def before_request(self):
        """
        """
        pass

    def after_request(self, response):
        """
        """
        return response