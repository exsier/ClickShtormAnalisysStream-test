from other.image_setting import *


# Определяем конец игры
def define_game_end(image, game_name):
    # Определяем игру
    if game_name == 'fifa':
        # Определяем текст
        result = im_rec(image, 27, 36, 6, 18)

        # Ищем кодовую фразу
        if result == 'завершить матч' or result == 'end match':
            return True
    elif game_name == 'nba':
        # Определяем текст
        result = im_rec(image, 35, 38, 4, 20, True).replace(' ', '')

        # Ищем кодовую фразу
        if result == 'завершить матч' or result == 'quitgameslals':
            return True
    elif game_name == 'nhl':
        # Определяем текст
        result = im_rec(image, 69, 72, 22, 32, True).replace(' ', '')

        # Ищем кодовую фразу
        if result == 'завершить матч' or result == 'finishgame':
            return True

    return False
