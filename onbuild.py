import debug
import copy
import config


def onbuild_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][4.1]_Вызов_onbuild_stage')
    config.ONBUILD_COUNT += 1
    # Копирование текущей инструкции
    copy.copy_stage(string, dockerfile)
    # проверка на наличие инструкции
    if "useradd" not in string[1]: # требуется переработка
        if debug.DEBUG:
            print('[DEBUG][4.2]_Сработало_условие_useradd_не_в_списке_аргументов')
        # Добавляем непревилигированного пользователя docker
        dockerfile.write(string[0] + " RUN groupadd -r docker\n")
        dockerfile.write(string[0] + " RUN useradd -r -g docker docker\n")
        dockerfile.write(string[0] + " USER docker\n")
    if debug.DEBUG:
        print('[DEBUG][4.3]_Выход_из_onbuild_stage')
