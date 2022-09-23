from other.settings import *
from other.bug_trap import bug_trap

import requests
import vk_api
import time

from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

user_token = VK_USER_TOKEN
group_id = VK_GROUP_ID
user_id = VK_USER_ID
album_id = VK_ALBUM_ID

# https://dev.vk.com/method

vk = vk_api.VkApi(api_version=5.131, token=user_token)


def get_vid_data(vid_name, vid_desc):
    try:
        time.sleep(0.01)
        while True:
            try:
                upload_data = vk.method('video.save', {
                    'name': str(vid_name),
                    'description': str(vid_desc),
                    'album_id': int(album_id),
                    'group_id': int(group_id)
                })
                break
            except Exception as e:
                print(e)
                time.sleep(5)
        return upload_data
    except Exception:
        bug_trap()


def upload_saved_vid(url, vid_id, vid_path):
    try:
        with open(vid_path, 'rb') as f:
            params = {'target_id': -group_id, 'album_id': album_id, 'owner_id': user_id, 'video_id': vid_id}
            time.sleep(0.01)
            requests.post(url, params=params, files={vid_path: f}, verify=False)
    except Exception:
        bug_trap()


def video_load(name, desc, vid_path):
    try:
        upload_data = get_vid_data(name, desc)
        url = upload_data.get('upload_url')
        vid_id = upload_data.get('video_id')
        upload_saved_vid(url, vid_id, vid_path)
        vid_url = f'https://vk.com/video/@public{group_id}?z=video-{group_id}_{vid_id}%2Fpl_-{group_id}_{album_id}'

        return vid_url
    except Exception:
        bug_trap()

