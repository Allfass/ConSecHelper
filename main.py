import sys
import preparation
import debug
import first_stage
import copy
import subprocess
import onbuild_stage


# Функция primer, вызывает другие функции, в зависимости от параметра
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
        with open(path_to_dockerfile, "r") as old_dockerfile:
            if old_dockerfile.readline().find('FROM') == -1:
                print('Это не dockerfile')
                exit(-2)
            # переход в начало
            old_dockerfile.seek(0)
            # Работа со строками в dockerfile
            current_line = old_dockerfile.readline()
            if debug.DEBUG:
                print('[DEBUG]', current_line.strip())
            splited_line = current_line.split(' ')
            docker_instruction = splited_line[0]
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
