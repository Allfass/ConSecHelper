import debug
import expose


# Функция копирует инструкцию в новый dockerfile
# Используется для инструкций, автоматическая обработка которых - затруднительна или невозможна
def copy_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][3.1]_Вызов_copy_stage')
    copy_string = ''
    for element in string:
        copy_string += element + ' '
    copy_string += '\n'
    if debug.DEBUG:
        print('[DEBUG][3.2]_Копируемая_строка_', copy_string)
    dockerfile.write(copy_string)
    if debug.DEBUG:
        print('[DEBUG][3.3]_Выход_из_copy_stage')
