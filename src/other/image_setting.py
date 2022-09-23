"""
Данный файл нужен для корректировки области где нужно распозднать текст
"""
import cv2
import easyocr

import warnings

# Отключаем UserWarning от Torchvision
warnings.filterwarnings("ignore", category=UserWarning)

reader = easyocr.Reader(["en"], gpu=True)


def im_rec(img, ht, hb, wl, wr, mode_size=False, mode_gray=False, mode_black=False):
    """
    img - изображение которое мы передаем в эту функцию, чтобы с ним взаимодействовать(изменять и считывать с него)
    ht - (сокращение от height top) это переменная которая показывает как будет обрезаться кадр относительно его верхней части
    hb - (сокращение от height bottom) это переменная которая показывает как будет обрезаться кадр относительно его нижней части
    wl - (сокращение от width left) это переменная которая показывает как будет обрезаться кадр относительно его левой части
    wr - (сокращение от width right) это переменная которая показывает как будет обрезаться кадр относительно его правой части
    mode_size - булевая переменная (boolean) в питоне это bool может принимать 2 значения True или False и взависимости от этой переменной к изображению либо будет либо не будет приминяться увеличение
    mode_gray - та же ... что и мод сайз(mode_size) только вместо изменения размера изображения эта штука может изменять цвет изображения превращая его в изображение состоящее из разных отенков серого
    mode_black - ...
    """

    edited = edit_image(img, ht, hb, wl, wr)

    if mode_size:
        edited = cv2.resize(edited, (0, 0), fx=2, fy=2)

    if mode_gray:
        edited = cv2.cvtColor(edited, cv2.COLOR_BGR2GRAY)

    if mode_black:
        _, edited = cv2.threshold(edited, 127, 255, cv2.THRESH_BINARY)

    result = reader.readtext(edited, detail=0, paragraph=True, batch_size=20)
    result_text = ' '.join(result).lower()

    return result_text


# Обрезаем изображения в процентах
def edit_image(image, h_top, h_down, w_lift, w_right, resize=1):
    # Размер изображения
    height = image.shape[0]
    width = image.shape[1]

    # Получаем процент из пикселей
    h_top = int(height / 100 * h_top)
    h_down = int(height / 100 * h_down)
    w_lift = int(width / 100 * w_lift)
    w_right = int(width / 100 * w_right)

    # Обрезаем изображение
    image = image[h_top:h_down, w_lift:w_right]

    # Изменяем размер
    image = cv2.resize(image, (0, 0), fx=resize, fy=resize)

    return image

def adding_name(image, left_player_name, right_player_name):
    try:
        #sav = img.copy()    

        #img = sav.copy()
        overlay = image.copy()
        font = cv2.FONT_HERSHEY_DUPLEX
        fontScale = 1
        label = f'{left_player_name} vs {right_player_name}'
        thickness = 2
        text_color = (255,255,255)
        text_width, text_height = cv2.getTextSize(label, font, fontScale, thickness)
        text_coord = (20,900 + 2 * text_width[1] - 10)
        cv2.rectangle(overlay, 
                (20, 900), (20 + text_width[0],  900 + 2 * text_width[1]),
                (0,0,0),
                -1)
        opacity = 1
        cv2.addWeighted(overlay, opacity, image, 0, 0, image)

        cv2.putText(image, label, text_coord, font, fontScale, text_color,thickness)

        return image
    except Exception as e:
        print(e)


class TrackBar:
    def __init__(self, window_name, name, min_number, max_number, value):
        # Название
        self.name = name
        # Мин значение
        self.min_number = min_number
        # Макс значение
        self.max_number = max_number
        # Название окна
        self.window_name = window_name

        # Создание трекбара
        cv2.createTrackbar(self.name, self.window_name, self.min_number, self.max_number, self.nothing)

        # Ставим стандартное значение
        cv2.setTrackbarPos(self.name, self.window_name, value)

    # Получить значение
    def get_value(self):
        return cv2.getTrackbarPos(self.name, self.window_name)

    # Измений значение
    def edit_value(self, value):
        cv2.setTrackbarPos(self.name, self.window_name, value)

    # Пустая функция для трекбара
    def nothing(self, x):
        pass


# Трекбар для просмотра куда области просмотра
class TrackBarImageSetting:
    def __init__(self, name):
        # Название окна
        self.setting_name = name
        cv2.namedWindow(self.setting_name, cv2.WINDOW_NORMAL)

        self.image_preview = f'{name} preview'
        cv2.namedWindow(self.image_preview, cv2.WINDOW_AUTOSIZE)

        # Для обрезания изображения
        self.h_top = TrackBar(self.setting_name, 'H(top)', 0, 100, 0)
        self.h_down = TrackBar(self.setting_name, 'H(down)', 1, 100, 100)
        self.w_left = TrackBar(self.setting_name, 'W(left)', 0, 100, 0)
        self.w_right = TrackBar(self.setting_name, 'W(right)', 1, 100, 100)

        # Для изменения размеров
        self.resize = TrackBar(self.setting_name, 'resize', 1, 20, 10)

        # Для теста
        self.test = TrackBar(self.setting_name, 'test.py', 0, 1, 0)

    # Получить значение для размера изображения из трекпада
    def track_resize_value(self):
        value = self.resize.get_value()

        if value < 1:
            value = 1
            self.resize.edit_value(value)

        value /= 10

        return value

    # Получаем значения для обрезания изобрания из трекпада
    def track_cut_value(self):
        # Берем значения из трекпада для обрезания
        h_top = self.h_top.get_value()
        h_down = self.h_down.get_value()
        w_left = self.w_left.get_value()
        w_right = self.w_right.get_value()

        if h_down <= 0:
            h_down = 1
            self.h_down.edit_value(h_down)

        if h_top >= h_down:
            h_top = h_down - 1
            self.h_top.edit_value(h_top)

        if w_right <= 0:
            w_right = 1
            self.w_right.edit_value(w_right)

        if w_left >= w_right:
            w_left = w_right - 1
            self.w_left.edit_value(w_left)

        return h_top, h_down, w_left, w_right

    # Обновляем изображение
    def update_image(self, image):
        # Изменяем изображение из значений трекпада
        cut_value = self.track_cut_value()
        resize_value = self.track_resize_value()
        image = edit_image(image, cut_value[0], cut_value[1], cut_value[2], cut_value[3], resize_value)

        # image = cv2.GaussianBlur(image, (5, 5), 0)
        # image = cv2.bilateralFilter(image, 9, 75, 75)

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # _, image = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)

        # result = reader.readtext(image, detail=0, paragraph=True, batch_size=20, text_threshold=0.5)
        # result = ' '.join(result).strip().lower()

        # print(result)

        # Обновляем кадр
        cv2.imshow(self.image_preview, image)
