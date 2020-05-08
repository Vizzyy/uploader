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
        for i in range(60):
            response_status = requests.get(f"https://api.gfycat.com/v1/gfycats/fetch/status/{gfyname}")
            result_json = response_status.json()
            print(f"Polling result: {result_json}")
            if 'gfyName' in result_json and result_json['gfyName'] != gfyname:
                print(f"Found existing match for video... {result_json['gfyName']}")
                gfyname = result_json['gfyName']
                break
            if 'task' in result_json and result_json['task'] == "complete":
                print("Encoding complete!")
                break
            time.sleep(5)

        # /v1/me/gfycats/{gfyId}/published	PUT	Update/replace the gfycat published. Params: 'value’, Values: '0’,'1’

        uri = f'https://thumbs.gfycat.com/{gfyname}-size_restricted.gif'
        print(f"Downloading GIF {uri} ...")
        with open(f'{local_filename[:-4]}.gif', 'wb') as f:
            f.write(requests.get(uri).content)
            print("Finished download!")

        local_gif = f'{local_filename[:-4]}.gif'
        return local_gif

    except Exception as e:
        print(e)
        return None
