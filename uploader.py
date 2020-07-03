import base64
from wcmatch import glob
import os
import shutil
from datetime import datetime
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError, ImgurClientRateLimitError
from config import *
from upload_video import *

# seconds to wait between uploads
# otherwise api rate-limiting fault
sleep_length = SLEEP_LENGTH
now = datetime.now()
print(f"{now} - Script started.\n")
client = ImgurClient(get_client_id(), get_client_secret(), get_access_token(), get_refresh_token())
today = str(datetime.date(now))


def upload_to_imgur(image_path, album_id):

    fd = open(image_path, 'rb')
    contents = fd.read()
    b64 = base64.b64encode(contents)
    data = {
        'image': b64,
        'type': 'base64',
        'album': album_id
    }
    fd.close()

    url = "https://imgur-apiv3.p.rapidapi.com/3/image"
    headers = client.prepare_headers()  # Set Auth Bearer header
    headers['x-rapidapi-host'] = RAPID_API_HOST
    headers['x-rapidapi-key'] = RAPID_API_KEY
    headers['content-type'] = "application/x-www-form-urlencoded"

    response = requests.request("POST", url, data=data, headers=headers)

    print(response.text)

    # Rate-limit check
    if response.status_code == 429:
        raise ImgurClientRateLimitError()

    try:
        response_data = response.json()
    except Exception as e:
        print(e)
        raise ImgurClientError('JSON decoding of response failed.')

    if 'data' in response_data and isinstance(response_data['data'], dict) and 'error' in response_data['data']:
        raise ImgurClientError(response_data['data']['error'], response.status_code)

    return response_data['data'] if 'data' in response_data else response_data


# check if finished folder exists
if not os.path.exists('finished_uploads'):
    print("creating finished_uploads directory...")
    os.makedirs('finished_uploads')

# check if album with today's date exists
response = client.get_account_albums(get_username())
today_album_exists = False
album_id = ""
for item in response:
    if item.title == today:
        print(f"Found album: {item.title} - {item.id}")
        today_album_exists = True
        album_id = item.id
        break

# otherwise create today's album
if not today_album_exists:
    album_config = {'title': today, 'privacy': 'hidden'}
    response = client.create_album(album_config)
    album_id = response['id']
    print(response)

# Glob together all files in directory that have these extension
full_list = glob.glob('*.{jpg,JPG,png,PNG,gif,GIF,mov,MOV,mp4,MP4}', flags=glob.BRACE)
list.sort(full_list)
print(f"There are {len(full_list)} images to parse.")

# while credits available, upload each file to album
image_config = {'album': album_id}
for image in full_list:
    try:
        now = datetime.now()
        file_extension = image[-4:].lower()
        print(f"{now} - Attempting to upload {image}, with file extension '{file_extension}'...")
        final_path = ""

        if file_extension == '.mp4' or file_extension == '.mov':
            print(f"Found video {image}; attempting to convert...")
            final_path = convert_to_gif(image)
            print(f"Gif name: {final_path}")
            shutil.move(image, "./finished_uploads/")
        else:
            final_path = image

        # response = client.upload_from_path(final_path, image_config, False)
        response = upload_to_imgur(final_path, album_id)
        print(response)
        print("Now moving file...")
        shutil.move(final_path, "./finished_uploads/")
    except ImgurClientError as e:
        print(e.error_message)
        print(e.status_code)
    except Exception as e:
        print(e)

    time.sleep(sleep_length)

now = datetime.now()
print(f"\n{now} - Script finished.\n")
