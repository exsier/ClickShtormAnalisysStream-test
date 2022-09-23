from other.image_setting import *


# Определяем игру
def define_game(image):
    # Убираем цвет из изображения
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Делаем кадр черно-белым
    _, black_while = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    # Ищем текст на изображении и объединяем все в 1 строку
    result = im_rec(black_while, 0, 100, 0, 100).replace(' ', '')
    
    # Список игр для определения
    game_list = {'sportsfifa22': 'fifa', 'sports4nm': 'nhl', 'everyoneeveryonecontentisg': 'nba'}
    # Кол-во найденных иг
    find_game_count = 0
    # Название найденной игры
    find_game = None

    # Смотрим название каких игр попали в кадр
    for key, value in game_list.items():
        if key in result:
            find_game_count += 1
            find_game = value

    # Если нашлась 1 игра из списка возвращаем успешный результат
    if find_game_count == 1:
        return find_game
    else:
        return None
