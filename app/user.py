from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id: str):
        self.id = user_id