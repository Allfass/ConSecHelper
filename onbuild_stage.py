def onbuild(string, dockerfile):
    # Используем непревилигированного пользователя
    dockerfile.write(string[0]+" RUN groupadd -r docker")
    dockerfile.write(string[0]+" RUN useradd -r -g docker docker")
