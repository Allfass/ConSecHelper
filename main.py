import sys
import preparation
import debug
from from_ import from_stage
from copy import copy_stage
import subprocess
from extend import final_stage
import expose
import config


# Функция primer, вызывает другие функции, в зависимости от параметра
# Каждая инструкция, полученная при парсинге dockerfile, вызывает функцию, указанную в значении ключа инструкции
# Для удобства каждая функция вынесена в отдельный модуль
# Название модуля соответствует инструкции
def primer(instruction):
    return {
        'FROM': from_stage,
        'RUN': copy_stage,
        'CMD': copy_stage,
        'LABEL': copy_stage,
        'MAINTAINER': copy_stage,
        'EXPOSE': expose.expose_stage,
        'ENV': copy_stage,
        'ADD': copy_stage,
        'COPY': copy_stage,
        'ENTRYPOINT': copy_stage,
        'VOLUME': copy_stage,
        'USER': copy_stage,
        'WORKDIR': copy_stage,
        'ARG': copy_stage,
        'ONBUILD': copy_stage,
        'STOPSIGNAL': copy_stage,
        'HEALTHCHECK': copy_stage,
        'SHELL': copy_stage
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
                    print('[DEBUG][0.2]_Текущая_инструкция_для_обработки=', current_line.strip())
                splited_line = current_line.split(' ')
                docker_instruction = splited_line[0]
                # Вызов Primer, в качестве параметров: список, содержащий команду и её параметр, и новый dockerfile
                primer(docker_instruction)(splited_line, new_dockerfile)
    except FileNotFoundError:
        print('Ошибка: Не найден файл docker')
    # Последний этап внесения изменений в dockerfile
    final_stage(new_dockerfile)
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
        cmd = 'docker run ' + expose_string + ' --memory=1G --memory-swap=2G --security-opt seccomp:default.json' \
                                              ' test_container:latest'
        if debug.DEBUG:
            print('[DEBUG][0.4]_command_to_run_container=', cmd)
        subprocess.call(cmd, shell=True)
    else:
        # Запуск контейнера
        subprocess.call(["docker", "run", "--memory=1G", "--memory-swap=2G",
                         "--security-opt", "seccomp:default.json", "test_container:latest"])
