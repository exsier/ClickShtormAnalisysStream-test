import sys
import os


# Ловушка ошибок
def bug_trap():
    exc_type = sys.exc_info()[0]
    exc_tb = sys.exc_info()[2]
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    text_error = f'Тип ошибки: {exc_type}\nПуть:\n     {file_name}({exc_tb.tb_lineno})'

    while exc_tb.tb_next is not None:
        exc_tb = exc_tb.tb_next
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        text_error += f' -> \n     {file_name}({exc_tb.tb_lineno})'

    print(text_error)