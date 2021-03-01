from config.config import connect_db
import os


def insert_to_db(file_name):
    curr = connect_db().cursor()
    sql = """INSERT INTO home_cover(cover_file, is_selected) 
            VALUES('{}', 0)""".format(file_name)
    curr.execute(sql)
    if curr:
        return {"database_status": "insert success"}
    else:
        return {"database_status": "insert failed"}


def list_home_cover():
    curr = connect_db().cursor()
    sql = """SELECT * FROM home_cover"""
    curr.execute(sql)
    items = []
    for i in curr:
        items.append(i)
    return items


def set_image(cover_id):
    curr = connect_db().cursor()
    sql_uncheck = "UPDATE home_cover SET is_selected = 0 WHERE is_selected = 1"
    curr.execute(sql_uncheck)
    sql_check = "UPDATE home_cover SET is_selected = 1 WHERE cover_id = {}".format(cover_id)
    curr.execute(sql_check)


def delete_image_cover(cover_id, path):
    curr = connect_db().cursor()
    sql_get = "SELECT * FROM home_cover WHERE cover_id = {}".format(cover_id)
    curr.execute(sql_get)
    home_cover_item = curr.fetchone()
    location = f"{path}{home_cover_item['cover_file']}"
    if os.path.exists(location):
        os.remove(location)
        sql = "DELETE FROM home_cover WHERE cover_id = {}".format(cover_id)
        curr.execute(sql)
        return {"status": "Deleted home cover image"}
    else:
        return {"status": "file does not exist"}
