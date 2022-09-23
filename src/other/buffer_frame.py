import os
import datetime

from threading import Thread
from other.api_request import get_usernames_id
from moviepy.editor import VideoFileClip, concatenate_videoclips

from define.game_score import *
from other.image_setting import edit_image, adding_name

import warnings

# Отключаем UserWarning от Torchvision
warnings.filterwarnings("ignore", category=UserWarning)

reader = easyocr.Reader(["en"], gpu=True)

def vids_unification(pc_list, game_id):
    flag = True
    for url in pc_list:
        if flag:
            clip1 = VideoFileClip(url)
            final_clip = concatenate_videoclips([clip1])
            flag = False
        else:
            clip1 = VideoFileClip(url)
            final_clip = concatenate_videoclips([final_clip, clip1])
    final_clip.write_videofile(f"result_clip_for{game_id}.mp4")
    return f"result_clip_for{game_id}.mp4"


# Сохраняем файл на диск
def save_video_file(path, frame_list, game_name, left_user_name, right_user_name):
    # Копируем в отдельный списко чтобы не было кофликтов
    if game_name == 'nhl':
        # Определяем на каком кадре был кол
        frame_goal = 0

        # Кол-во пропускаемых кадров
        max_analysis_frame = 5
        # Счетчик кадров
        analysis_frame = 0

        # Проходимся по всему видео и ищем слово гол
        for frame in frame_list:
            if analysis_frame > max_analysis_frame:
                # Ищем слово гол в кадре
                frame = edit_image(frame, 20, 80, 20, 80)
                frame = cv2.resize(frame, (0, 0), fx=0.7, fy=0.7)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
                result = reader.readtext(frame, detail=0, paragraph=True, batch_size=20)
                result = ' '.join(result).lower()

                if re.match(r'((^goal$)|(^goal\s)|(\sgoal$)|(\sgoal\s))', result):
                    break

                analysis_frame = 0

            analysis_frame += 1
            frame_goal += 1

        # Начальный кадр хайлайта
        first_frame = frame_goal - 150

        if first_frame < 0:
            first_frame = 0

        # Конечный кадр хайлайта
        last_frame = frame_goal + 150

        if last_frame > len(frame_list):
            last_frame = len(frame_list)

        frame_list = frame_list[first_frame:last_frame].copy()
    else:
        # Копируем последние 10 сек
        frame_list = frame_list[-len(frame_list) // 3:].copy()

    # Разрешение видео
    frame_size = (1920, 1080)
    # Кол-во кадров
    fps = 30
    # Формат записи
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Создаем нужный видео файл
    file = cv2.VideoWriter(path, fourcc, fps, frame_size)

    # Записываем в файл кадры
    for frame in frame_list:

        frame = adding_name(frame, f'{left_user_name}', f'{right_user_name}')
        file.write(frame)

    # Сохраняем видео
    file.release()


# Буфер видео кадров.
# Хранит последние n кадров, чтобы после изменения счета склеить из них хайлайт.
class BufferFrame:
    def __init__(self):
        # Буфер кадров
        self.buffer_frame_list = []

        # Папка куда записываются видео
        self.path = ''

        # Текущая игра
        self.game_name = None

    # Добавляем в буфер кадр
    def update(self, frame, key, save=False):
        # Устаревшие кадры
        if len(self.buffer_frame_list) >= 900:
            self.buffer_frame_list.pop(0)

        # Добавляем новый кадр
        self.buffer_frame_list.append(frame)

        # Получаем имена игроков
        usernames = get_usernames_id(key)

        # Сохраняем видео из буфера
        if save:
            # Копируем буфер в отдельную переменную
            frame_list = self.buffer_frame_list.copy()

            # Смотрим текущее время для названия файла
            date = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            # Директория папки
            dir_path = f'{self.path}{key}/'
            # Директория файла
            file_path = f'{dir_path}{date}.avi'

            # Проверяем наличие отдельной папки потока для видео
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)

            # Вызываем функцию записи видео
            Thread(target=save_video_file, args=(file_path, frame_list, self.game_name, usernames[0], usernames[1])).start()

            return file_path


# Старая логика по сохранению видео 0.1
"""
# Копируем в отдельный списко чтобы не было кофликтов
if self.game_name == 'nhl':
    # У NHL счет обновляется спустя 10 секунд после гола
    frame_list = self.buffer_frame_list[:len(self.buffer_frame_list) // 3].copy()
else:
    # Копируем последние 10 сек
    frame_list = self.buffer_frame_list[len(self.buffer_frame_list) // 3:].copy()

# Смотрим текущее время для названия файла
date = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
# Директория папки
dir_path = f'{self.path}{key}/'
# Директория файла
file_path = f'{dir_path}{date}.avi'

# Проверяем наличие отдельной папки потока для видео
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)

# Вызываем функцию записи видео
Thread(target=save_video_file, args=(file_path, frame_list)).start()

return file_path
"""
