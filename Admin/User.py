from config.config import connect_db
import datetime


def list_user():
    items = []
    curr = connect_db().cursor()
    sql = "SELECT id as user_id, name, email FROM users"
    curr.execute(sql)

    for i in curr:
        items.append(i)

    return items


def edit_user(name, email, userid):
    curr = connect_db().cursor()
    update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """UPDATE users SET name='{}', email='{}', updated_at = '{}' 
            WHERE id = {}""".format(name, email, update_date, userid)
    curr.execute(sql)


def create_user(name, email, password):
    curr = connect_db().cursor()
    sql = """INSERT INTO users(name, email, password) 
            VALUES('{}', '{}', "{}")""".format(name, email, password)
    curr.execute(sql)
