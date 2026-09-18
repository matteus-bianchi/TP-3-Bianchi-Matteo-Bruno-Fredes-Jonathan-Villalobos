import json
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

VIDEO_FILE = "forge_short.mp4"


def authenticate():
    client_secret = json.loads(
        os.environ["YOUTUBE_CLIENT_SECRET"]
    )

    # El JSON descargado por Google puede tener "installed"
    # como clave principal.
    config = client_secret.get(
        "installed",
        client_secret.get("web")
    )

    credentials = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri=config["token_uri"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        scopes=SCOPES,
    )

    return credentials


def upload_video():
    credentials = authenticate()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    request_body = {
        "snippet": {
            "title": "Cómo instalar Forge y mods en Minecraft",
            "description": (
                "Tutorial rápido para instalar Forge "
                "y agregar mods a Minecraft Java Edition."
            ),
            "tags": [
                "Minecraft",
                "Forge",
                "Mods",
                "Tutorial",
                "Minecraft Java"
            ],
            "categoryId": "20"
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        VIDEO_FILE,
        mimetype="video/mp4",
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = request.execute()

    print("===================================")
    print("VIDEO SUBIDO CORRECTAMENTE")
    print("ID:", response["id"])
    print(
        "URL: https://www.youtube.com/watch?v="
        + response["id"]
    )
    print("===================================")


if __name__ == "__main__":
    upload_video()