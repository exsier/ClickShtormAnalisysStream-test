from other.image_setting import *

from other.bug_trap import bug_trap

import easyocr
import cv2
import re

import warnings

# Отключаем UserWarning от Torchvision
warnings.filterwarnings("ignore", category=UserWarning)


# Включаем easyocr
reader = easyocr.Reader(["en"], gpu=True)


# Определяем счет в играх
def define_game_information(frame, game_name, game_mode):
    # Выбираем в какой игре определять счет
    if game_name == 'nba':
        # Определяем счет в nba
        result = define_nba_information(frame, game_mode)
    elif game_name == 'nhl':
        # Определяем счет в nhl
        result = define_nhl_information(frame)
    elif game_name == 'fifa':
        result = define_fifa_information(frame, game_mode)
    else:
        # Неизвестная игра
        result = None

    # Проверяем состоит ли счет из 2 цифр
    if result is not None:
        # Возвращаем счет 2 команд
        return result[0], result[1]
    else:
        return None


# Определяем счет в FIFA
def define_fifa_information(img, game_mode):
    try:
        # Определяем счет в режиме volt
        if game_mode == 'volt':
            frame = edit_image(img, 5, 9, 8, 26)
            frame = cv2.resize(frame, (0, 0), fx=3, fy=3)
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            frame = cv2.bilateralFilter(frame, 9, 75, 75)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

            result_list = reader.readtext(frame, batch_size=100, text_threshold=0.7, detail=0)

            for result in result_list:
                if re.match(r'^\d+-\d$', result):
                    return int(result.split('-')[0]), int(result.split('-')[1])
        # Определяем счет в классическом режиме
        elif game_mode == 'classic':
            frame = cv2.resize(img, (0, 0), fx=3, fy=3)
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            frame = cv2.bilateralFilter(frame, 9, 75, 75)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

            # Список возможных вариантов где может располагаться счет
            game_score_position_list = [
                # America 7 11 15 20
                (7, 11, 15, 20),
                # England 10 12 11 16
                (10, 12, 11, 16),
                # France 7 11 22 31
                (7, 11, 22, 31),
                # Germany 8 14 13 21
                (8, 14, 13, 21),
                # Spain 6 10 20 26
                (6, 10, 20, 26),
                # Standard 5 8 18 21
                (5, 8, 18, 21)
            ]

            # Проверяем все позиции счетов
            for game_score_position in game_score_position_list:
                game_score = edit_image(frame, *game_score_position)
                result = reader.readtext(game_score, batch_size=100, text_threshold=0.8, detail=0)
                result = ' '.join(result)

                if re.match(r'^\d+(\s|\S)+\d+$', result):
                    return int(re.findall(r'^\d+', result)[0]), int(re.findall(r'\d+$', result)[0])
    except Exception:
        bug_trap()
        return None


# Определяем счет в NHL
def define_nhl_information(img):
    try:
        # Просто число
        # 95, 100, 38, 43
        result_left = edit_image(img, 95, 100, 38, 43)
        result_left = cv2.resize(result_left, (0, 0), fx=3, fy=3)

        result_left = cv2.GaussianBlur(result_left, (5, 5), 0)
        result_left = cv2.bilateralFilter(result_left, 9, 75, 75)

        result_left = reader.readtext(result_left, detail=0, paragraph=True, batch_size=20, text_threshold=0.6)
        result_left = ' '.join(result_left).strip().lower()

        if len(result_left.split(' ')) > 1:
            result_left = result_left.split(' ')[1]

        # Просто число
        # 95, 100, 57, 61
        result_right = edit_image(img, 95, 100, 57, 61)

        result_right = cv2.resize(result_right, (0, 0), fx=3, fy=3)
        result_right = cv2.cvtColor(result_right, cv2.COLOR_BGR2GRAY)
        _, result_right = cv2.threshold(result_right, 127, 255, cv2.THRESH_BINARY)
        result_right = reader.readtext(result_right, detail=0, paragraph=True, batch_size=20, text_threshold=0.8)
        result_right = ' '.join(result_right)

        # Проверяем валидность опеределения счета
        if re.match(r'^\S+ \d+$', result_left) and re.match(r'\d+ ^\S+$', result_right[0]):
            # Возвращаем полученный счет
            return int(result_left[1]), int(result_right[0])
        else:
            return None
    except Exception:
        bug_trap()
        return None


# Определяем счет в NBA
def define_nba_information(img, game_mode):
    try:
        # Смотрим текущий режим
        if game_mode == 'classic':
            result_left = im_rec(img, 86, 91, 85, 88)
            result_right = im_rec(img, 91, 96, 85, 88)

            # Проверяем валидность опеределения счета
            if re.match(r'\d+', result_left) and re.match(r'\d+', result_right):
                # Возвращаем полученный счет
                return int(result_left), int(result_right)
            else:
                # Возвращаем ошибку
                return None
        elif game_mode == "blacktop":
            # Вырезаем счет команд
            text = im_rec(img, 90, 98, 55, 94)
            # Проверяем валидность определения счета
            if re.match(r'\d\d \d\d', text):
                # Возвращаем полученный счет
                return int(text.split()[0]), int(text.split()[1])
            else:
                return None
    except Exception:
        bug_trap()
        return None


# Определить финальный счет из nba blacktop
def final_score_nba_blacktop(image):
    try:
        result_left = im_rec(image, 73, 80, 13, 19)
        result_right = im_rec(image, 73, 81, 81, 88)

        if re.match(r'\d+', result_left) and re.match(r'\d+', result_right):
            return int(result_left), int(result_right)
        else:
            return None
    except Exception:
        bug_trap()
        return None
