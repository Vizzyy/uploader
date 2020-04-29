import glob
import os
import sys
import shutil
from datetime import datetime
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from config import *

client_id = get_client_id()
client_secret = get_client_secret()
access_token = get_access_token()
refresh_token = get_refresh_token()
username = get_username()

client = ImgurClient(client_id, client_secret, access_token, refresh_token)

today = str(datetime.date(datetime.now()))

try:
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
    response = client.get_account_albums(username)
    today_album_exists = False
    album_id = ""
    for item in response:
        print(f"{item.title} - {item.id}")
        if item.title == today:
            today_album_exists = True
            album_id = item.id
            break

    # otherwise create today's album
    if not today_album_exists:
        album_config = {'title': today, 'privacy': 'hidden'}
        response = client.create_album(album_config)
        album_id = response['id']
        print(response)

    # glob files in directory
    fullList = glob.glob('*.jpg')
    print(f"There are {len(fullList)} images to parse.")

    # while credits available, upload each file to album
    image_config = {'album': album_id}
    for image in fullList:
        if curr_credits['UserRemaining'] < 10 or curr_credits['ClientRemaining'] < 100:
            print("Reached API limit!")
            break
        print(f"Attempting to upload {image} ...")
        response = client.upload_from_path(image, image_config, False)
        print(response)
        print("Now moving file...")
        shutil.move(image, "./finished_uploads/")

except ImgurClientError as e:
    print(e.error_message)
    print(e.status_code)

print("Script finished.")
