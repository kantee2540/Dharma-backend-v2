from config.config import connect_db


def home_cover():
    curr = connect_db().cursor()
    sql = "SELECT cover_file FROM home_cover WHERE is_selected = 1"
    curr.execute(sql)
    item = curr.fetchone()
    file = item["cover_file"]
    return file
