from wcmatch import glob
import os
import sys
import shutil
from datetime import datetime
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from config import *
from upload_video import *

# seconds to wait between uploads
# otherwise api rate-limiting fault
sleep_length = 75
now = datetime.now()
print(f"{now} - Script started.\n")
client = ImgurClient(get_client_id(), get_client_secret(), get_access_token(), get_refresh_token())

today = str(datetime.date(now))

# check credit limit, if none exit
curr_credits = ImgurClient.get_credits(client)
print(curr_credits)
if curr_credits['UserRemaining'] < 10 or curr_credits['ClientRemaining'] < 100:
    print("API LIMIT REACHED")
    sys.exit()

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

        response = client.upload_from_path(final_path, image_config, False)
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
