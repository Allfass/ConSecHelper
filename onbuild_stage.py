def onbuild(string, dockerfile):
    # проверка на наличие инструкции
    if "useradd" in string[1]:
        # выполняем копирование
        dockerfile.write(string[0], ' ', string[1])
    else:
        # выполняем копирование
        dockerfile.write(string[0], ' ', string[1])
        # Добавляем непревилигированного пользователя
        dockerfile.write(string[0]+" RUN groupadd -r docker")
        dockerfile.write(string[0]+" RUN useradd -r -g docker docker")
