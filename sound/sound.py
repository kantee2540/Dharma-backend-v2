from config.config import connect_db


def list_sound():
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds ORDER BY updated_at DESC"""
    curr.execute(sql)

    items = []
    for i in curr:
        items.append(i)

    return items


def list_sound_limit(limit):
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds ORDER BY updated_at DESC LIMIT {}""".format(limit)
    curr.execute(sql)

    items = []
    for i in curr:
        items.append(i)

    return items


def get_sound_package_info(sound_id):
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds WHERE id = {}""".format(sound_id)
    curr.execute(sql)
    info = curr.fetchone()
    return info


def list_sound_file(sound_id):
    curr = connect_db().cursor()
    sql = """SELECT * FROM sounds_file WHERE package_id = {}""".format(sound_id)
    curr.execute(sql)
    info = get_sound_package_info(sound_id)
    items = []

    for i in curr:
        items.append(i)

    json_array = {}
    if info is not None:
        json_array.update(info)
        json_array.update({"data": items})
    else:
        json_array.update({
            "error": "item not found",
            "code": 404
        })

    return json_array
