import debug


# Функция копирует инструкцию в новый dockerfile
# Используется для инструкций, автоматическая обработка которых - затруднительна или невозможна
def copy_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][3.1]_Вызов_copy_stage')
    copy_string = ''
    for element in string:
        copy_string += element + ' '
    strip_string = copy_string.strip()
    strip_string += '\n'
    if debug.DEBUG:
        print('[DEBUG][3.2]_Копируемая_строка_', strip_string)
    dockerfile.write(strip_string)
    if debug.DEBUG:
        print('[DEBUG][3.3]_Выход_из_copy_stage')
