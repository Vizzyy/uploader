import requests

import sys
from datetime import datetime
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from config import *

client = ImgurClient(get_client_id(), get_client_secret(), get_access_token(), get_refresh_token())
now = datetime.now()
print(f"{now} - Script started.")

try:
    source_album_id = sys.argv[1]
    images = client.get_album_images(source_album_id)
    sorted_images = sorted(images, key=lambda x: x.datetime, reverse=False)
    ids = []
    for image in sorted_images:
        ids.append(image.id)

    # API only accepts comma separated list of IDs
    formatted_id = str(ids.__str__()).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

    album_config = {
        'ids': formatted_id
    }

    print(album_config)

    url = "https://api.imgur.com/3/album/"+source_album_id

    response = requests.request("POST", url, headers=client.prepare_headers(), data=album_config)

    print(response.text.encode('utf8'))

except ImgurClientError as e:
    print(e.error_message)
    print(e.status_code)
except Exception as e:
    print(e)

now = datetime.now()
print(f"{now} - Script finished.")
