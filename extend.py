import debug


def onbuild_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][4.1]_Вызов_onbuild_stage')
    # проверка на наличие инструкции
    if debug.DEBUG:
        print('[DEBUG][4.2]_Внесение_финальных_команд_RUN_USER')
    # Добавляем непревилигированного пользователя docker
    dockerfile.write("ONBUILD RUN groupadd -r docker\n")
    dockerfile.write("ONBUILD RUN useradd -r -g docker docker\n")
    dockerfile.write("ONBUILD USER docker\n")
    if debug.DEBUG:
        print('[DEBUG][4.3]_Выход_из_onbuild_stage')
