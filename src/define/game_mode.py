import re

from other.image_setting import *


# Определяем режим игры
def define_game_mode(image, game_name):
    # Определяем режим для FIFA
    if game_name == 'fifa':
        # Обрезаем кадр с местом, где описан режим
        image_result = edit_image(image, 3, 8, 43, 57)

        # Увеличиваем кадр в 2 раза
        image_result = cv2.resize(image_result, (0, 0), fx=2, fy=2)

        # Делаем черно-белым
        image_result = cv2.cvtColor(image_result, cv2.COLOR_BGR2GRAY)
        _, image_result = cv2.threshold(image_result, 127, 255, cv2.THRESH_BINARY)

        # Получаем текст с кадра
        result = im_rec(image_result, 0, 100, 0, 100).replace(' ', '')
        # Определяем какой это режим
        if result == 'classicmatch':
            return 'classic'
        elif result in ['3v3rush', '4v4', '4v4rush', '5v5', 'futsal', 'survival']:
            return 'volt'

        return None
    # Определяем режим для NBA
    elif game_name == 'nba':
        # Ищем счет
        result_blacktop = im_rec(image, 87, 98, 78, 94).replace(' ', '')
        result_classic = im_rec(image, 86, 96, 85, 98, True)

        # Проверяем условия счета
        if re.search(r'\w+ \d+ \d+ \w+ \w+ \d+(.|:)\d', result_classic):
            return 'classic'
        elif re.match(r'\w{16}\d{2}\d{2}', result_blacktop):
            return 'blacktop'
        else:
            return None

    elif game_name == 'nhl':
        # Ищем счет
        result = im_rec(image, 58, 66, 39, 61)
        # Проверяем условия счета
        if result == 'start game':
            return 'classic'
        else:
            return None
    return None
