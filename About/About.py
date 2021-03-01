from config.config import connect_db


def about():
    curr = connect_db().cursor()
    sql = "SELECT * FROM about WHERE is_selected = 1"
    curr.execute(sql)
    data = curr.fetchone()
    return data
