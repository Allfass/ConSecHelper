import subprocess
import os
import debug


# Функция для создание файла с настройками работы auditd
def audit_config():
    if debug.DEBUG:
        print('[DEBUG]_Внесение изменений в конфигурационный файл auditd')
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


def docker_preparation():
    # Этап подготовки хоста к генерации файла
    # Создание/получение имени нового пользователя
    while True:
        choice_username = input('Вы хотите создать нового пользователя, для взаимодействия с контейнерами(Yes/No)?:')
        if choice_username[0] == 'Y' or choice_username[0] == 'y':
            docker_username = input('Введите имя пользователя docker?:')
            subprocess.call(["useradd", "-c", docker_username, "-m", "-c", "/bin/bash", docker_username])
            subprocess.call(["usermod", "-aG", "sudo", docker_username])
            subprocess.call(["usermod", "-aG", "docker", docker_username])
            break
        else:
            docker_username = input('Введите имя существующего пользователя, который будет работать с контейнерами:')
            if debug.DEBUG:
                print('[DEBUG][DOCKER_USERNAME]-', docker_username)
            # Проверка наличия пользователя в системе
            user_list_call = subprocess.run(["cut", "-d:", "-f1", "/etc/passwd"], stdout=subprocess.PIPE, text=True)
            if user_list_call.stdout.find(docker_username) >= 0:
                if debug.DEBUG:
                    print('[DEBUG]Сработало условие, пользователь существует в списке пользователей')
                subprocess.call(["usermod", "-aG", "sudo", docker_username])
                subprocess.call(["usermod", "-aG", "docker", docker_username])
                break
    # установка и конфигурация auditd
    call = subprocess.run(["dpkg", "-l"], stdout=subprocess.PIPE, text=True)
    if call.stdout.find('auditd') < 0:
        user_choice = input('Вы хотите использовать auditd для контроля вызовов(Да/Нет)?')
        if user_choice[0] == 'Y' or user_choice[0] == 'y':
            if debug.DEBUG:
                print('[DEBUG]_Установка auditd')
            subprocess.run(["apt", "update"])
            subprocess.run(["apt", "install", "auditd", "-y"])
            auditd()
    else:
        print('auditd уже установлен')
        auditd()
    # Прослушивание по умолчанию только unix-сокет
    subprocess.call(["dockerd", "-H", "\"unix:///var/run/docker.sock\""])
    # Установка Docker bench security
    print('Вы хотите установить docker benchmark?')
    subprocess.call(["git", "clone", "https://github.com/docker/docker-bench-security.git"])
    subprocess.call(["cd", "docker-bench-security"])
    docker_bench_report = subprocess.run(["sh", "docker-bench-security.sh"], stdout=subprocess.PIPE, text=True)
    subprocess.call(["cd", ".."])
    report_file = open("docker_bench_report", "w")
    if debug.DEBUG:
        print("[DEBUG] writing docker benchmark results")
    report_file.write(docker_bench_report.stdout)
    if debug.DEBUG:
        print("[DEBUG] done")


