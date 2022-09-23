from threading import Thread
from define.game_score import define_game_information as dgi
from define.game_score import *
from define.game import define_game
from define.game_mode import define_game_mode
from define.game_end import define_game_end
from other.api_request import *
from other.buffer_frame import BufferFrame
from other.bug_trap import bug_trap

from other.settings import *

from collections import Counter

import datetime
import time
import cv2

import warnings

# Отключаем UserWarning
warnings.filterwarnings("ignore", category=UserWarning)


class AnalysisStream:
    def __init__(self, ip: str, key: str, port=1935):
        # Адрес откуда получать трансляцию
        self.rtmp_url = f"rtmp://{ip}:{port}/live/{key}"
        # Ключ подключения к трансляции
        self.key = key

        # Статус подключения
        self.connection_status = False
        # Последний сохраненный кадр
        self.last_frame = None

        # Название текущей игры
        self.game_name = None
        # Название текущей игры
        self.game_mode_name = None
        # Счет игры
        self.game_score_1 = None
        self.game_score_2 = None

        
        # Переменная которая определяет нужно ли нам сканировать тип игры, тип режима, конец игры
        self.need_to_def = True
        
        # Время начла игры
        self.game_start_time = None

        # Буфер последних кадров (для записи хайлайтов)
        self.buffer = BufferFrame()

        # Список адресов файла где хранятся хайлайты
        # Данный список нужен для загрузки данных файлов вк после конца матча
        self.highlight_file_link_list = []

        # Дект событий
        self.goal_detected = False

        # Режим дебага
        self.debug = APP_DEBUG

        """
        Запуск микро сервисов
        """
        # Начинаем анализировать стрим
        Thread(target=self.main).start()
        # Определитель игры
        Thread(target=self.define_game_func).start()
        # Определитель режима игры
        Thread(target=self.define_game_mode_func).start()
        # Определитель игры
        Thread(target=self.define_game_end_func).start()
        # Определяем счет
        Thread(target=self.define_game_information_func).start()

    # Определитель игры
    def define_game_func(self):
        while True:
            if self.need_to_def:
                # Проверяем наличие кадра для анализа
                if type(self.last_frame).__name__ != 'NoneType':
                    # Определяем игру
                    result = define_game(self.last_frame)

                    # Проверяем статус обнаружения игры
                    if result is not None:
                        # Если игра не является текущей игрой обновляем данные
                        if self.game_name != result:
                            # DEBUG
                            if self.debug:
                                print(f'Текущая игра поменялась: {result}')

                            # Обновляем таймер
                            self.clear_game_info()

                            # Записываем текущую игру
                            self.game_name = result
                            self.buffer.game_name = result
            time.sleep(0.01)

    # Определитель режима игры
    def define_game_mode_func(self):
        while True:
            if self.need_to_def:
                # Проверяем наличие кадра для анализа
                if type(self.last_frame).__name__ != 'NoneType':
                    # Результат определенного режима
                    result = define_game_mode(self.last_frame, self.game_name)

                    # Проверяем корректность пришедших данных
                    if result is not None:
                        # Проверяем изменился ли режим
                        if self.game_mode_name != result:
                            # Изменяем название режима
                            self.game_mode_name = result

                            # DEBUG
                            if self.debug:
                                print(f'Текущий режим поменялся: {result}')

                            # Очищаем информацию по прошлой игре
                            self.clear_game_info()

                        # Обнуляем время пока пользователь выбирает режим
                        if self.game_name in ['fifa', 'nhl']:
                            self.clear_game_info()
            time.sleep(0.01)

    # Определитель счета
    def define_game_information_func(self):
        # Список последних пришедших счетов
        last_score = []
        # Длина буфера счета
        len_last_score = 20
        # Кол-во одинаковых элементов для корректировки
        len_same_score = 15

        while True:
            if type(self.last_frame).__name__ != 'NoneType':
                # Результат обработки кадра и счет (score1, score2)
                result = dgi(self.last_frame, self.game_name, self.game_mode_name)

                # Проверяем корректность пришедших данных
                if result is not None:
                    self.need_to_def = False
                    # Если счет пустой значит игра только началась
                    if self.game_score_1 is None:
                        self.start_game_timer()

                        # Обнуляем счет
                        self.game_score_1 = 0
                        self.game_score_2 = 0

                    # Определяем изменения счета
                    if result[0] != self.game_score_1 or result[1] != self.game_score_2:
                        # Проверяем корректность пришедших данных (NBA)
                        if self.game_name == 'nba':
                            # Счет должен изменится от 1 до 3, а второй не изменится
                            if result[0] - self.game_score_1 in [1, 2, 3] and result[1] == self.game_score_2:
                                # Записоваем хайлайт
                                self.save_highlight()
                                i = 1
                                # DEBUG
                                if self.debug:
                                    print(f'ГОЛ! {result[0]}-{result[1]}')

                                # Изменяем счет
                                self.game_score_1 = result[0]

                                # Ставим на паузу
                                time.sleep(0.5)
                            # Счет должен изменится от 1 до 3, а второй не изменится
                            elif result[1] - self.game_score_2 in [1, 2, 3] and result[0] == self.game_score_1:
                                # Записоваем хайлайт
                                self.save_highlight()
                                i = 1
                                # DEBUG
                                if self.debug:
                                    print(f'ГОЛ! {result[0]}-{result[1]}')

                                # Изменяем счет
                                self.game_score_2 = result[1]

                                # Ставим на паузу
                                time.sleep(0.5)
                            else:
                                # Удаляем старые значения
                                if len(last_score) > len_last_score:
                                    last_score.pop(0)

                                # Добавляем не корректный результат
                                last_score.append(result)

                                if Counter(last_score).most_common()[0][1] >= len_same_score:
                                    result = Counter(last_score).most_common()[0][0]

                                    self.game_score_1 = result[0]
                                    self.game_score_2 = result[1]

                                    if self.debug:
                                        print(f"Корректировка счета: {self.game_score_1} {self.game_score_2}")

                                    last_score.clear()
                                
                        # Проверяем корректность пришедших данных (NHL, FIFA)
                        elif self.game_name in ['nhl', 'fifa']:
                            # Счет должен изменится на 1
                            if result[0] == self.game_score_1 + 1 and result[1] == self.game_score_2:
                                # Записываем хайлайт
                                self.save_highlight()
                                i = 1
                                # DEBUG
                                if self.debug:
                                    print(f'ГОЛ! {result[0]}-{result[1]}')

                                # Изменяем счет
                                self.game_score_1 = result[0]
                            # Счет должен изменится на 1
                            elif result[1] == self.game_score_2 + 1 and result[0] == self.game_score_1:
                                # Записываем хайлайт
                                self.save_highlight()
                                i = 1
                                # DEBUG
                                if self.debug:
                                    print(f'ГОЛ! {result[0]}-{result[1]}')

                                # Изменяем счет
                                self.game_score_2 = result[1]
                            # Проверка не некоректные значения
                            else:
                                # Удаляем старые значения
                                if len(last_score) > len_last_score:
                                    last_score.pop(0)

                                # Добавляем не корректный результат
                                last_score.append(result)

                                if Counter(last_score).most_common()[0][1] >= len_same_score:
                                    result = Counter(last_score).most_common()[0][0]

                                    self.game_score_1 = result[0]
                                    self.game_score_2 = result[1]

                                    if self.debug:
                                        print(f"Корректировка счета: {self.game_score_1} {self.game_score_2}")

                                    last_score.clear()
                else:
                    self.need_to_def = True
            time.sleep(0.001)

    # Определитель конца матча
    def define_game_end_func(self):
        while True:
            # Проверяем наличие кадра для анализа
            if type(self.last_frame).__name__ != 'NoneType':
                # Проверяем наличие конца игры
                result = define_game_end(self.last_frame, self.game_name)

                # Проверяем корректность даннх
                if result:
                    # Проверяем начался ли матч
                    if self.game_start_time is not None:
                        # Доп. хайлайт для NBA режим blacktop
                        if self.game_mode_name == 'blacktop':
                            # Записываем хайлайт
                            self.save_highlight()

                            # Ждем итоговое статистику
                            for i in range(60):
                                # Ищем конечный счет
                                result = final_score_nba_blacktop(self.last_frame)

                                # Если получили результат записываем его
                                if result is not None:
                                    self.game_score_1 = result[0]
                                    self.game_score_2 = result[1]
                                    break

                                time.sleep(0.5)

                            # DEBUG
                            if self.debug:
                                print(f'Игра закончилась со счетом {result[0]}-{result[1]}')

                        # Определяем итоговое время матча
                        game_final_time = datetime.datetime.now() - self.game_start_time

                        # Узнаем id игры
                        game_id = post_req(
                            self.key,
                            self.game_start_time,
                            game_final_time,
                            self.game_name,
                            self.game_mode_name,
                            self.game_score_1,
                            self.game_score_2
                        )

                        # DEBUG
                        if self.debug:
                            print(self.highlight_file_link_list)

                        # Копируем
                        pc_list = self.highlight_file_link_list.copy()
                        game_name = self.game_name
                        print(1)
                        Thread(target=sending_vids, args=(pc_list, game_id, game_name)).start()
                    self.clear_game_info()
            time.sleep(0.01)

    # Основной цикл
    def main(self):
        try:
            if self.debug:
                print('Ожидание подключения к стриму')

            # Подключаемся в стриму
            stream = cv2.VideoCapture(self.rtmp_url, cv2.CAP_FFMPEG)

            # Проверяем статус подключения
            if not stream.read()[0]:
                # Подключаемся еще раз
                self.main()
            else:
                # Основной цикл
                while True:
                    # Получаем статус и картинку
                    status, img = stream.read()

                    if status:
                        # Изменяем статус подключения
                        if not self.connection_status:
                            self.connection_status = True

                            if self.debug:
                                print('Подключение установлено')

                        # Записываем последний кадр
                        self.last_frame = img

                        # Проверка нужно ли записать хайлайт
                        if self.goal_detected:
                            self.goal_detected = False

                            # Сохранить видео
                            path_video_file = self.buffer.update(self.last_frame, self.key, True)

                            # Записываем адресс файла
                            # Данный список нужен для загрузки данных файлов в вк после конца матча
                            self.highlight_file_link_list.append(path_video_file)
                        else:
                            # Записываем последний кадр в буфер
                            self.buffer.update(self.last_frame, self.key)
                    cv2.waitKey(1)
        except Exception as e:
            bug_trap()

    # Записать хайлайт
    def save_highlight(self):
        # Ставим в положение True, для другого потока
        self.goal_detected = True

    # Очищаем данные матча
    def clear_game_info(self):
        # Очищаем список адресами файлами
        self.highlight_file_link_list.clear()

        # Очищаем время матча
        self.game_start_time = None

        # Очищаем счет
        self.game_score_1 = None
        self.game_score_2 = None

    # Запускаем таймер начала игры
    def start_game_timer(self):
        self.game_start_time = datetime.datetime.now()

    # Начать смотреть стрим (для тестов)
    def show(self):
        # Ждем подключения
        if self.connection_status:
            track_bar = TrackBarImageSetting('test')

            # Бесконечный чикл с обновлением картинки
            while True:
                track_bar.update_image(self.last_frame)

                cv2.waitKey(1)
        else:
            time.sleep(1)
            self.show()


if __name__ == '__main__':
    key = input("Введите ключ трансляции:")
    AnalysisStream(APP_IP, key.strip())
