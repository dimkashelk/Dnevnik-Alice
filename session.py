from data import db_session, users


class Session:

    def __init__(self):
        db_session.global_init('db/users.db')
        self.session = db_session.create_session()

    def insert_new_user(self, user_id):
        user = users.User(
            id=user_id
        )
        self.session.add(user)
        self.session.commit()

    def get_token(self, user_id):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        return user.token

    def get_user(self, user_id):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        return user

    def set_token(self, user_id, token):
        user = self.get_user(user_id)
        if user is None:
            self.insert_new_user(user_id)
            user = self.get_user(user_id)
        user.token = token
        self.session.commit()

    def commit(self):
        self.session.commit()
