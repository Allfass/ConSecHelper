import sys
import preparation
import debug
import first_stage


# Функция primer, вызывает другие функции, в зависимости от параметра
def primer(instruction):
    return {
        'FROM': first_stage.from_stage,
        'RUN': None,
        'CMD': None,
        'LABEL': None,
        'MAINTAINER': None,
        'EXPOSE': None,
        'ENV': None,
        'ADD': None,
        'COPY': None,
        'ENTRYPOINT': None,
        'VOLUME': None,
        'USER': None,
        'WORKDIR': None,
        'ARG': None,
        'ONBUILD': None,
        'STOPSIGNAL': None,
        'HEALTHCHECK': None,
        'SHELL': None
    }.get(instruction, 'error')


if __name__ == '__main__':
    preparation.docker_user()
    preparation.auditd()
    # Этап внесения изменений в конфигурацию Dockerfile
    # Создание нового dockerfile
    new_dockerfile = open('Dockerfile.new', 'w')
    # Считывание директории с файлом и проверка на наличие аргумента
    path_to_dockerfile = ''
    try:
        path_to_dockerfile = sys.argv[1]
    except IndexError:
        print('Отсутствует аргумент с путем к файлу docker')
    # проверка на наличие первого оператора в файле
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
        primer(docker_instruction)(splited_line, old_dockerfile)
    # Закрытие Dockerfile
    new_dockerfile.close()
