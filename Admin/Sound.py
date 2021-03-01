from config.config import connect_db
import datetime
import os
import shutil


def list_sound():
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds ORDER BY updated_at DESC"""
    curr.execute(sql)

    items = []
    for i in curr:
        items.append(i)

    return items


def create_sound_package(name, root_path):
    curr = connect_db().cursor()
    folder_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(root_path, folder_date)
    os.mkdir(path)
    sql = """INSERT INTO sounds(sound_package_name, sound_package_folder) 
            VALUES('{}', '{}')""".format(name, folder_date)
    curr.execute(sql)


def sound_detail(sound_id):
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds WHERE id = {}""".format(sound_id)
    curr.execute(sql)
    item = curr.fetchone()
    if item is not None:
        sound_items = []
        sql = "SELECT * FROM sounds_file WHERE package_id = {}".format(sound_id)
        curr.execute(sql)
        for i in curr:
            sound_items.append(i)
        item.update({"data": sound_items})
    return item


def update_package_name(name, sound_id):
    curr = connect_db().cursor()
    sql = """UPDATE sounds SET sound_package_name = '{}'
            WHERE id = {}""".format(name, sound_id)
    curr.execute(sql)


def upload_cover(sound_id, file_name):
    curr = connect_db().cursor()
    sql = """UPDATE sounds SET package_image = '{}' 
            WHERE id = {}""".format(file_name, sound_id)
    curr.execute(sql)


def upload_sound_file(sound_id, files_name):
    curr = connect_db().cursor()
    for j in files_name:
        sql = "INSERT INTO sounds_file(package_id, sound_file) VALUE({}, '{}')".format(sound_id, j)
        curr.execute(sql)


def get_sound_file(sound_file_id):
    curr = connect_db().cursor()
    sql = "SELECT * FROM sounds_file WHERE sound_id = {}".format(sound_file_id)
    curr.execute(sql)
    item = curr.fetchone()
    return item


def delete_sound(sound_id, sound_file_id, root_path):
    curr = connect_db().cursor()
    file_data = get_sound_file(sound_file_id)
    if file_data is not None:
        file_location = root_path + file_data["sound_file"]
        if os.path.exists(file_location) and file_data is not None:
            os.remove(file_location)
            sql = """DELETE FROM sounds_file
                    WHERE sound_id = {} AND package_id = {}""".format(sound_file_id, sound_id)
            curr.execute(sql)
            return {"status": "Delete success"}
        else:
            return {"status": "file not exist"}
    else:
        return {"status": "file not exist"}


def delete_package(sound_id, root_path):
    curr = connect_db().cursor()
    if os.path.exists(root_path):
        shutil.rmtree(root_path)
        sql = "DELETE FROM sounds WHERE id = {}".format(sound_id)
        curr.execute(sql)
        return {"status": "Deleted folder and data"}
    else:
        return {"status": "Package does not exist"}
