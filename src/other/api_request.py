import json
import requests
import os
from other.settings import *
from other.vk_connection_api import video_load
from other.buffer_frame import vids_unification


# Аддрес сервера
url = f'http://{APP_DJANGO_IP}:{APP_DJANGO_PORT}/api/v1'


# Функция пот отправке запросов с данными по игре
def post_req(key, start_time, time, game, mode, score_1, score_2):
    connection_id = get_connection_id(key)
    player_list_of_id = get_player_id(connection_id)

    data = {
        "player_id_left": player_list_of_id[0],
        "player_id_right": player_list_of_id[1],
        "player_score_left": score_1,
        "player_score_right": score_2,
        "game_time_start": str(start_time),
        "game_time": str(time),
        "game_name": game,
        "game_mode": mode,
        "connection": connection_id
    }
    game_request = json.loads(requests.post(url + "/game_list", data=data, verify=False).text)

    return game_request.get("id")


# Получаем id соединения
def get_connection_id(connection_key):
    connections_list = json.loads(requests.get(url + '/connection_list', verify=False).text).get('results')
    for connection in connections_list:
        if connection.get('key_connection') == connection_key:
            return connection.get('id')

def get_usernames_id(connection_key):
    connections_list = json.loads(requests.get(url + '/connection_list', verify=False).text).get('results')
    for connection in connections_list:
        if connection.get('key_connection') == connection_key:
            return connection.get('name_left_user'), connection.get('name_right_user')

# Получаем id игрока
def get_player_id(connection_id):
    connection = json.loads(requests.get(url + f'/connection/{connection_id}', verify=False).text)

    return connection.get("id_left_user"), connection.get("id_right_user")


# Функция пот отправке запросов с хайлайтами
def send_game_highlights(game_id, highlight_list):
    for highlight_link in highlight_list:
        data = {
            "link": highlight_link,
            "game": game_id
        }

        requests.post(url + "/highlight_list", data=data, verify=False)


def sending_vids(pc_list, game_id, game_name):
    try:
        highlight_list_vk_link = []

        result_video = vids_unification(pc_list, game_id)

        pc_list.append(result_video)
        highlight_list_vk_link.append(video_load(result_video, game_name, result_video))

        # Удаление файлов при необходимости
        for file in pc_list:
            os.remove(file)

        send_game_highlights(game_id, highlight_list_vk_link)
    except Exception:
        bug_trap()
