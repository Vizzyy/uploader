import sys
from datetime import datetime
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from config import *

client = ImgurClient(get_client_id(), get_client_secret(), get_access_token(), get_refresh_token())
now = datetime.now()
print(f"{now} - Script started.")

# CLI Args
# 1 source album id
# 2 destination album name
try:
    source_album_id = sys.argv[1]
    dest_album_title = sys.argv[2]
    images = client.get_album_images(source_album_id)
    sorted_images = sorted(images, key=lambda x: x.datetime, reverse=False)
    ids = []
    for image in sorted_images:
        ids.append(image.id)

    # API only accepts comma separated list of IDs
    formatted_id = str(ids.__str__()).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

    album_config = {
        'title': dest_album_title,
        'privacy': 'hidden',
        'ids': formatted_id
    }

    print(album_config)
    response = client.create_album(album_config)
    print(response)

except ImgurClientError as e:
    print(e.error_message)
    print(e.status_code)
except Exception as e:
    print(e)

now = datetime.now()
print(f"{now} - Script finished.")
