import debug
import copy


def onbuild_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][4.1]_Вызов_onbuild_stage')
    # проверка на наличие инструкции
    copy.copy_stage(string, dockerfile)
    if "useradd" not in string[1]:
        # Добавляем непревилигированного пользователя docker
        dockerfile.write(string[0] + " RUN groupadd -r docker\n")
        dockerfile.write(string[0] + " RUN useradd -r -g docker docker\n")
    if debug.DEBUG:
        print('[DEBUG][4.2]_Выход_из_onbuild_stage')
