import config
import debug
import copy


# Функция передает в глобальную переменную номер порта и протокол,
# После чего переносит инструкцию и аргумент в новый dockerfile
def expose_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][5.1]_Вызов_expose_stage')
    split_string = string[1].split('/')
    # удаление специальных символов
    for element in range(len(split_string)):
        new_string = split_string[element].replace('\n', '')
        if debug.DEBUG:
            print('[DEBUG][5.3]_Строка_без_спецсимволов_', new_string)
        split_string[element] = new_string
    string[1] = string[1].replace('\n', '')
    config.EXPOSE_PARAMETER.append(split_string[0]+':'+string[1])
    if debug.DEBUG:
        print('[DEBUG][5.4]_глобальная_переменная_EXPOSE_PARAMETR=', config.EXPOSE_PARAMETER)
    copy.copy_stage(string, dockerfile)
    if debug.DEBUG:
        print('[DEBUG][5.5]_Выход_expose_stage')


# Преобразует список в строку
def concate_exposes(expose_list):
    if debug.DEBUG:
        print('[DEBUG][5.6]_Вызов_concate_exposes')
    command_string = ''
    for element in expose_list:
        command_string += '-p ' + element + ' '
    if debug.DEBUG:
        print('[DEBUG][5.7]_Результат_конкатенации_', command_string)
    if debug.DEBUG:
        print('[DEBUG][5.8]_Выход_concate_exposes')
    return command_string


