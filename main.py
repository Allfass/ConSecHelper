import subprocess
import sys
import os
import json


# Этап проверки образа для инструкции FROM из Dockerfile
def from_stage(docker_image):
    subprocess.call(["curl", "https://static.snyk.io/cli/latest/snyk-linux", "-o", "snyk"])
    subprocess.call(["chmod", "+x", "./snyk"])
    subprocess.call(["./snyk", "auth"])
    call_container_test = subprocess.run(["./snyk", "container", "test", docker_image,
                                          "--severity-threshold=high", "--json"], stdout=subprocess.PIPE, text=True)
    data = json.loads(call_container_test.stdout)
    if data.get('summary') == 'No high or critical severity vulnerabilities':
        print(docker_image, 'проверен и получен из надежного источника')
        return docker_image
    else:
        # Формирование отчета по уязвимостям
        report = open("report_" + docker_image + ".txt", "w")
        report.write(data)
        report.close()
        # Формирование образа на замену уязвимому
        buffer_message = ''
        counter = 1
        for item in data['docker']['baseImageRemediation']['advice']:
            if counter == 0:
                buffer_message = item['message']
            if item['message'] == 'Major upgrades':
                counter = 0
        second_buffer = buffer_message.split('\n')
        third_buffer = second_buffer[1].split(' ')
        recommended_image = third_buffer[0]
        print(recommended_image)
        return recommended_image


# Функция для создание файла с настройками работы auditd
def audit_config():
    auditd_config_file = open('audit.rules', 'w')
    auditd_config_file.write("""
                auditctl -w /usr/bin/dockerd -p rwxa -k docker
                auditctl -w /run/containerd -k docker
                auditctl -w /var/lib/docker -k docker
                auditctl -w /etc/docker -k docker
                auditctl -w /lib/systemd/system/docker service -k docker
                auditctl -w /lib/systemd/system/docker .socket -k docker
                auditctl -w /etc/default/docker -k docker
                auditctl -w /etc/docker/daemon.json -k docker
                auditctl -w /usr/bin/docker-containerd -k docker
                auditctl -w /usr/bin/docker-runc -k docker
                auditctl -w /us/bin/containerd -k docker
                auditctl -w /usr/bin/containerd-shim -k docker
                auditctl -w /usr/bin/containerd-shim-runc-v1 -k docker
                auditctl -w /usr/bin/containerd-shim-runc-v2 -k docker
            """)
    auditd_config_file.close()
    subprocess.call(["systemctl", "restart", "auditd"])


# Внесение правил для аудита доступа к конфигурационным файлам Docker
def auditd():
    print('Внесение изменений в конфигурационный файл auditd')
    # Проверка наличия директории для файла настроек
    if os.path.exists('/etc/audit/rules.d/'):
        os.chdir('/etc/audit/rules.d/')
        audit_config()
    else:
        subprocess.call(["mkdir", "-p", "/etc/audit/rules.d/"])
        os.chdir('/etc/audit/rules.d/')
        audit_config()


if __name__ == '__main__':
    # Этап подготовки хоста к генерации файла
    # Создание/получение имени нового пользователя
    while True:
        docker_username = ''
        choice_username = input('Вы хотите создать нового пользователя, для взаимодействия с контейнерами(Yes/No)?:')
        if choice_username[0] == 'Y' or choice_username[0] == 'y':
            docker_username = input('Введите имя пользователя docker?:')
            subprocess.call(["useradd", "-c", docker_username, "-m", "-c", "/bin/bash", docker_username])
            break
        else:
            docker_username = input('Введите имя существующего пользователя, который будет работать с контейнерами:')

            # Проверка наличия пользователя в системе
            user_list_call = subprocess.run(["cut", "-d:", "-f1", "/etc/passwd"], stdout=subprocess.PIPE, text=True)
            print(user_list_call.stdout.find(docker_username))
            if user_list_call.stdout.find(docker_username) >= 0:
                break
    subprocess.call(["usermod", "-aG", "sudo", docker_username])
    subprocess.call(["usermod", "-aG", "docker", docker_username])

    # установка и конфигурация auditd
    call = subprocess.run(["dpkg", "-l"], stdout=subprocess.PIPE, text=True)
    if call.stdout.find('auditd') < 0:
        user_choice = input('Вы хотите использовать auditd для контроля вызовов(Да/Нет)?')
        if user_choice[0] == 'Y' or user_choice[0] == 'y':
            subprocess.run(["apt", "update"])
            subprocess.run(["apt", "install", "auditd", "-y"])
            auditd()
    else:
        print('auditd уже установлен')
        auditd()

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
    with open(path_to_dockerfile, "r") as file1:
        if file1.readline().find('FROM') == -1:
            print('Это не dockerfile')
            exit(-2)

        # итерация по строкам
        file1.seek(0)
        for line in file1:
            print(line.strip())
