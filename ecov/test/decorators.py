"""Useful reusable django decorators

"""
def log_user(function):
    """Decorator that connects the test user before doing other tests
    """
    def decorate(self):
        self.login()
        return function(self)
    return decorate
