import time
import requests


def convert_to_gif(local_filename: str) -> str:
    """ Using public gfycat API, convert incoming .mov or .mp4 into .gif format """
    try:
        # local_filename = "IMG_0012.MOV"  # sys.argv[1]

        files = {'file': open(local_filename, 'rb')}

        # curl -v -XPOST https://api.gfycat.com/v1/gfycats -H "Content-Type: application/json"

        headers = {'Content-Type': 'application/json'}
        response_initial = requests.post("https://api.gfycat.com/v1/gfycats", headers=headers)
        print(response_initial.json())
        gfyname = response_initial.json()['gfyname']

        # curl -i https://filedrop.gfycat.com --upload-file ./gfyname

        payload = {'key': gfyname}
        response_upload = requests.post("https://filedrop.gfycat.com", files=files, data=payload)
        print("file uploaded!")
        print(response_upload.text)
        time.sleep(2)

        # GET https://api.gfycat.com/v1/gfycats/fetch/status/gfyname
        # {'task': 'complete', 'gfyname': 'gfyname'}
        gif_link = ""
        while True:
            response_status = requests.get(f"https://api.gfycat.com/v1/gfycats/fetch/status/{gfyname}")
            print(response_status.json())
            upload_status = response_status.json()['task']
            if upload_status == "complete":
                break
            time.sleep(5)

        # /v1/me/gfycats/{gfyId}/published	PUT	Update/replace the gfycat published. Params: 'value’, Values: '0’,'1’

        print("Downloading GIF...")
        uri = f'https://thumbs.gfycat.com/{gfyname}-size_restricted.gif'
        with open(f'{local_filename[:-4]}.gif', 'wb') as f:
            f.write(requests.get(uri).content)
            print("Finished download!")

        local_gif = f'{local_filename[:-4]}.gif'
        return local_gif

    except Exception as e:
        print(e)
        return None
