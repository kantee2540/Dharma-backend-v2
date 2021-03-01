from config.config import connect_db
import hashlib


def get_user(username):
    curr = connect_db().cursor()
    sql = """SELECT * FROM users WHERE email = '{}' """.format(username)
    curr.execute(sql)
    user = curr.fetchone()
    if user is not None:
        return user
    else:
        return None


def get_current_user(token):
    curr = connect_db().cursor()
    sql = """SELECT * FROM access_token a, users u
            WHERE a.token = '{}'""".format(token)
    curr.execute(sql)
    user = curr.fetchone()
    if user is not None:
        return user
    else:
        return None


def get_token(user_id, secret):
    curr = connect_db().cursor()
    sql = "SELECT * FROM access_token WHERE user_id = {}".format(user_id)
    curr.execute(sql)
    token = curr.fetchone()
    hashed = hashlib.sha256(secret).hexdigest()
    if token is None:
        sql = "INSERT INTO access_token(token, user_id) VALUES('{}', {})".format(hashed, user_id)
        curr.execute(sql)
    else:
        sql = "UPDATE access_token SET token = '{}' WHERE user_id = {} ".format(hashed, user_id)
        curr.execute(sql)

    return hashed

