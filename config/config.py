import pymysql
import json

with open("config.json") as configs:
    config = json.load(configs)


def connect_db():
    connection = pymysql.connect(host=config["host_database"],
                                 user=config["user"],
                                 password=config["password"],
                                 db=config["database"],
                                 charset="utf8mb4",
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)

    return connection
