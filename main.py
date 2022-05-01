import sys
import preparation
import debug
import first_stage
import copy
import subprocess
import onbuild_stage


# Функция primer, вызывает другие функции, в зависимости от параметра
# Каждая инструкция, полученная при парсинге dockerfile, вызывает функцию, указанную в значении ключа инструкции
# Для удобства каждая функция вынесена в отдельный модуль
# Название модуля соответствует инструкции
def primer(instruction):
    return {
        'FROM': first_stage.from_stage,
        'RUN': None,
        'CMD': copy.copy_stage,
        'LABEL': copy.copy_stage,
        'MAINTAINER': copy.copy_stage,
        'EXPOSE': copy.copy_stage,
        'ENV': copy.copy_stage,
        'ADD': copy.copy_stage,
        'COPY': copy.copy_stage,
        'ENTRYPOINT': copy.copy_stage,
        'VOLUME': copy.copy_stage,
        'USER': None,
        'WORKDIR': copy.copy_stage,
        'ARG': None,
        'ONBUILD': onbuild_stage,
        'STOPSIGNAL': None,
        'HEALTHCHECK': copy.copy_stage,
        'SHELL': None
    }.get(instruction, 'error')


if __name__ == '__main__':
    # Предварительный этап: подготовка хостовой машины, установки дополнительных утилит (при желании)
    preparation.docker_preparation()
    # Этап внесения изменений в конфигурацию Dockerfile
    # Создание нового dockerfile
    new_dockerfile = open('Dockerfile', 'a')
    # Считывание директории с файлом и проверка на наличие аргумента
    path_to_dockerfile = sys.argv[1]
    if debug.DEBUG:
        print('[DEBUG]', path_to_dockerfile)
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
            current_line = old_dockerfile.readline()
            if debug.DEBUG:
                print('[DEBUG]', current_line.strip())
            splited_line = current_line.split(' ')
            docker_instruction = splited_line[0]
            # Вызов Primer, в качестве параметров: список, содержащий команду и её параметр, и новый dockerfile
            primer(docker_instruction)(splited_line, new_dockerfile)
    except FileNotFoundError:
        print('Ошибка: Не найден файл docker')
    # Закрытие Dockerfile
    new_dockerfile.close()
    # Сборка образа
    subprocess.call(["docker", "build", "-t", "test_container", "."])
    # Запуск контейнера
    subprocess.call(["docker", "run", "-u", "docker", "--memory=2G", "--memory-swap=1G", "--security-opt",
                     "seccomp:default.json", "test_container"])
