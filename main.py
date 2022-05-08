import sys
import preparation
import debug
import from_
import copy
import subprocess
import onbuild
import expose
import config
from run import run_stage # переписать импорты, добавить инструкции


# Функция primer, вызывает другие функции, в зависимости от параметра
# Каждая инструкция, полученная при парсинге dockerfile, вызывает функцию, указанную в значении ключа инструкции
# Для удобства каждая функция вынесена в отдельный модуль
# Название модуля соответствует инструкции
def primer(instruction):
    return {
        'FROM': from_.from_stage,
        'RUN': run_stage,
        'CMD': copy.copy_stage,
        'LABEL': copy.copy_stage,
        'MAINTAINER': copy.copy_stage,
        'EXPOSE': expose.expose_stage,
        'ENV': copy.copy_stage,
        'ADD': copy.copy_stage,
        'COPY': copy.copy_stage,
        'ENTRYPOINT': copy.copy_stage,
        'VOLUME': copy.copy_stage,
        'USER': copy.copy_stage,
        'WORKDIR': copy.copy_stage,
        'ARG': copy.copy_stage,
        'ONBUILD': onbuild.onbuild_stage,
        'STOPSIGNAL': copy.copy_stage,
        'HEALTHCHECK': copy.copy_stage,
        'SHELL': copy.copy_stage
    }.get(instruction, 'error')


if __name__ == '__main__':
    # Предварительный этап: подготовка хостовой машины, установки дополнительных утилит (при желании)
    preparation.docker_preparation()
    # Этап внесения изменений в конфигурацию Dockerfile
    # Создание нового dockerfile
    new_dockerfile = open('Dockerfile.new', 'a')
    # Считывание директории с файлом и проверка на наличие аргумента
    path_to_dockerfile = sys.argv[1]
    if debug.DEBUG:
        print('[DEBUG][0.1]', path_to_dockerfile)
    # проверка на наличие первого оператора в файле
    try:
        # Открытие файла для чтения
        with open(path_to_dockerfile, "r") as old_dockerfile:
            # Проверка на наличие инструкции FROM в первой строчке
            if old_dockerfile.readline().find('FROM') == -1:
                print('Это не dockerfile')
                # Если его нет - выход из программы
                exit(-2)
            # переход указателя в начало файла
            old_dockerfile.seek(0)
            # Работа со строками в dockerfile
            for current_line in old_dockerfile:
                if debug.DEBUG:
                    print('[DEBUG][0.2]', current_line.strip())
                splited_line = current_line.split(' ')
                docker_instruction = splited_line[0]
                # Вызов Primer, в качестве параметров: список, содержащий команду и её параметр, и новый dockerfile
                primer(docker_instruction)(splited_line, new_dockerfile)
    except FileNotFoundError:
        print('Ошибка: Не найден файл docker')
    # Закрытие Dockerfile
    new_dockerfile.close()
    # Переименование текущего файла в Dockerfile.old, нового файла в Dockerfile
    subprocess.call(["mv", "Dockerfile", "Dockerfile.old"])
    subprocess.call(["mv", "Dockerfile.new", "Dockerfile"])
    # Сборка образа
    subprocess.call(["docker", "build", "-t", "test_container", "."])
    expose_string = expose.concate_exposes(config.EXPOSE_PARAMETER)
    if debug.DEBUG:
        print('[DEBUG][0.2]_expose_list=', expose_string)
    # Проверка наличия агументов expose
    if config.EXPOSE_PARAMETER:
        if debug.DEBUG:
            print('[DEBUG][0.3]_Сработало_условие_EXPOSE_PARAMETER_содержит_элементы')
        # Запуск контейнера с открытыми портами
        subprocess.call(["docker", "run", "-u", "docker", expose_string, "--memory=2G", "--memory-swap=1G",
                         "--security-opt", "seccomp:default.json", "test_container"])
    else:
        # Запуск контейнера
        subprocess.call(["docker", "run", "-u", "docker", "--memory=2G", "--memory-swap=1G",
                         "--security-opt", "seccomp:default.json", "test_container"])
