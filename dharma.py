from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, File, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List
import uvicorn
import bcrypt
import json
import datetime
from Home import Home
from Admin import Cover, User, Sound
from About import About
from sound import sound
from Auth.Auth import get_user, get_token, get_current_user

# Load config
with open("config.json") as configs:
    config = json.load(configs)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/file", StaticFiles(directory=config["resource_directory"]), name="static")


def authorization(token):
    ex_token = token.split(" ")
    if ex_token[0] == "Bearer":
        user = get_current_user(ex_token[1])
        if user is not None:
            return True
        else:
            return False
    else:
        return False


@app.get("/")
def welcome():
    return {
        "app_name": "พระไตรปิฎกใกล้ตัว",
        "version": 2.0
    }


@app.get("/sound")
async def index(limit: int = 0):
    if limit:
        list_sound = sound.list_sound_limit(limit)
    else:
        list_sound = sound.list_sound()
    return list_sound


@app.get("/sound/{sound_id}")
async def sound_file(sound_id: int = 0):
    list_sound_file = sound.list_sound_file(sound_id=sound_id)
    return list_sound_file


@app.get("/home/cover")
def home_cover(request: Request):
    file_item = Home.home_cover()
    cover_url = "{}file/home_cover/{}".format(request.base_url, file_item)
    return {"cover": cover_url}


@app.get("/about")
def about():
    about_item = About.about()
    return about_item


##############################################################################################################
# ADMIN API
@app.post("/admin/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth = {}
    user = get_user(form_data.username)
    password = form_data.password.encode("utf8")
    client_id = form_data.client_id
    client_secret = form_data.client_secret.encode("utf8")
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if client_id != config["client_id"]:
        raise HTTPException(status_code=400, detail="Incorrect client id")

    user_pass = user["password"].encode("utf-8")
    token = get_token(user["id"], client_secret)
    if bcrypt.checkpw(password, user_pass):
        auth.update({"name": user["name"]})
        auth.update({"email": user["email"]})
        auth.update({"token": token})
        auth.update({"status": "Success"})
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return auth


@app.post("/admin/check_user")
def check_user(Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    else:
        return {"message": "Token OK"}


@app.get("/admin/sound")
def list_sound(Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    sound_item = Sound.list_sound()
    return sound_item


@app.get("/admin/sound/{id}")
def sound_detail(id, Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    item = Sound.sound_detail(id)
    if item is not None:
        return item
    else:
        return {
            "id": id,
            "error": "item not found"
        }


@app.post("/admin/sound/create")
def create_sound_package(name: str = Form(...),
                         Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    Sound.create_sound_package(name, config["resource_directory"]+"/")
    return {
        "name": name,
        "status": "Created sound package"
    }


@app.post("/admin/sound/{id}/upload_cover")
def upload_cover(id,
                 image_file: UploadFile = File(...),
                 Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    sound_package = Sound.sound_detail(id)
    if sound_package is None:
        raise HTTPException(status_code=404, detail="Not found")
    path = sound_package["sound_package_folder"]
    file_name = image_file.filename
    location = f"{config['resource_directory']}/{path}/{file_name}"
    with open(location, "wb+") as file_obj:
        file_obj.write(image_file.file.read())
    Sound.upload_cover(id, file_name)
    return {
        "id": id,
        "status": "Upload package image success"
    }


@app.post("/admin/sound/{id}/edit_name")
def edit_name(id,
              name: str = Form(...),
              Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    Sound.update_package_name(name, id)
    return{
        "id": id,
        "status": "Updated package name success",
    }


@app.post("/admin/sound/{id}/upload_sound")
def upload_sound(id, files: List[UploadFile] = File(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    sound_package = Sound.sound_detail(id)
    if sound_package is None:
        raise HTTPException(status_code=404, detail="Not found")
    path = sound_package["sound_package_folder"]
    file_name_list = []
    for file in files:
        file_name = file.filename
        file_name_list.append(file_name)
        location = f"{config['resource_directory']}/{path}/{file_name}"
        with open(location, "wb+") as file_obj:
            file_obj.write(file.file.read())
    Sound.upload_sound_file(id, file_name_list)

    return {
        "id": id,
        "status": "Uploaded complete",
        "files": files
    }


@app.post("/admin/sound/{id}/delete")
def delete_sound(id, sound_id: int = Form(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    sound_package = Sound.sound_detail(id)
    if sound_package is None:
        raise HTTPException(status_code=404, detail="Not found")
    path = sound_package["sound_package_folder"]
    result = Sound.delete_sound(id, sound_id, f"{config['resource_directory']}/{path}/")
    return result


@app.post("/admin/sound/delete")
def delete_package(sound_id: int = Form(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    sound_package = Sound.sound_detail(sound_id)
    if sound_package is None:
        raise HTTPException(status_code=404, detail="Not found")
    path = sound_package["sound_package_folder"]
    result = Sound.delete_package(sound_id, f"{config['resource_directory']}/{path}")
    return result


@app.post("/admin/user")
def list_user(Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_items = User.list_user()

    return user_items


@app.post("/admin/user/edit")
def edit_user(name: str = Form(...),
              email: str = Form(...),
              user_id: str = Form(...),
              Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")

    User.edit_user(name, email, user_id)
    return {
        "user_id": user_id,
        "status": "Update user success"
    }


@app.post("/admin/user/create")
def create_user(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    encode_password = password.encode("utf8")
    hashed = bcrypt.hashpw(encode_password, bcrypt.gensalt()).decode(encoding="utf8")
    User.create_user(name, email, hashed)
    return {
        "name": name,
        "email": email,
        "status": "create user success"
    }


@app.get("/admin/cover")
def list_home_cover(Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    items = Cover.list_home_cover()
    return items


@app.post("/admin/upload_cover")
def upload_cover(request: Request, file: UploadFile = File(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")

    date = datetime.datetime.now()
    ex_file_name = file.filename.split(".")

    formatted = date.strftime("%d-%m-%Y_%H-%M-%S")
    file_name = "{}_{}.{}".format(ex_file_name[0], formatted, ex_file_name[1])
    location = f"{config['resource_directory']}/home_cover/{file_name}"

    with open(location, "wb+") as file_obj:
        file_obj.write(file.file.read())

    insert_db_state = Cover.insert_to_db(file_name)

    result = {
        "file_name": file_name,
        "path": "{}file/home_cover/{}".format(request.base_url, file_name),
        "database": insert_db_state
    }

    return result


@app.post("/admin/select_image")
def select_image(cover_id: int = Form(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    Cover.set_image(cover_id)
    return{
        "cover_id": cover_id,
        "status": "Update default cover success"
    }


@app.post("/admin/delete_image_cover")
def delete_image_cover(cover_id: int = Form(...), Authorization: Optional[str] = Header('')):
    authorize = authorization(Authorization)
    if not authorize:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = Cover.delete_image_cover(cover_id, f"{config['resource_directory']}/home_cover/")
    result.update({"cover_id": cover_id})
    return result


if __name__ == '__main__':
    # initial app
    uvicorn.run("dharma:app", host="127.0.0.1", port=8080)
