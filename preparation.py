import subprocess
import os
import debug


# Функция для создание файла с настройками работы auditd
def audit_config():
    if debug.DEBUG:
        print('[DEBUG][1.8.1]_Внесение изменений в конфигурационный файл auditd_config()')
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
    if debug.DEBUG:
        print('[DEBUG][1.8.2]_Закрытие_конфигурационного_файла_auditd')
    subprocess.call(["systemctl", "restart", "auditd"])


# Внесение правил для аудита доступа к конфигурационным файлам Docker
def auditd():
    if debug.DEBUG:
        print('[DEBUG][1.8.1]_Внесение изменений в конфигурационный файл auditd')
    print('Внесение изменений в конфигурационный файл auditd')
    # Проверка наличия директории для файла настроек
    if os.path.exists('/etc/audit/rules.d/'):
        if debug.DEBUG:
            print('[DEBUG][1.9.2]_Сработало_вхождение_путь_к_rules.d_существует')
        os.chdir('/etc/audit/rules.d/')
        audit_config()
    else:
        if debug.DEBUG:
            print('[DEBUG][1.9.3]_Сработало_вхождение_путь_к_rules.d_не_существует')
        subprocess.call(["mkdir", "-p", "/etc/audit/rules.d/"])
        os.chdir('/etc/audit/rules.d/')
        audit_config()
    if debug.DEBUG:
        print('[DEBUG][1.10.4]_Внесение изменений в конфигурационный файл auditd')


def docker_preparation():
    if debug.DEBUG:
        print('[DEBUG][1.1]_Вызов_docker_preparation')
    # Остановка всех запущенных контейнеров
    cmd = 'docker stop $(docker ps -a -q)'
    echo = subprocess.Popen(cmd, shell=True)
    # Ожидание окончания работы команды
    echo.wait()
    if debug.DEBUG:
        if echo.returncode == 0:
            print('[DEBUG][1.2]_Остановка_запущенных_процессов_завершилась_с_кодом_0')
        else:
            print('[DEBUG][1.2]_Остановка_запущенных_процессов_завершилась_с_кодом_', echo.returncode)
    # Этап подготовки хоста к генерации файла
    # Создание/получение имени нового пользователя
    while True:
        choice_username = input('Вы хотите создать нового пользователя, для взаимодействия с контейнерами(Yes/No)?:')
        if choice_username[0] == 'Y' or choice_username[0] == 'y':
            if debug.DEBUG:
                print('[DEBUG][1.3]_Сработало_вхождение_создание_нового_пользователя')
            docker_username = input('Введите имя пользователя docker?:')
            subprocess.call(["useradd", "-c", docker_username, "-m", "-c", "/bin/bash", docker_username])
            if debug.DEBUG:
                print('[DEBUG][1.4]_Создан_пользователь_', docker_username)
            subprocess.call(["usermod", "-aG", "sudo", docker_username])
            subprocess.call(["usermod", "-aG", "docker", docker_username])
            if debug.DEBUG:
                print('[DEBUG][1.5]_Пользователь_', docker_username, '_внесен_в_группы_sudo_docker')
            break
        else:
            docker_username = input('Введите имя существующего пользователя, который будет работать с контейнерами:')
            # Проверка наличия пользователя в системе
            user_list_call = subprocess.run(["cut", "-d:", "-f1", "/etc/passwd"], stdout=subprocess.PIPE, text=True)
            if user_list_call.stdout.find(docker_username) >= 0:
                if debug.DEBUG:
                    print('[DEBUG][1.3] - Сработало условие, пользователь существует в списке пользователей')
                subprocess.call(["usermod", "-aG", "sudo", docker_username])
                subprocess.call(["usermod", "-aG", "docker", docker_username])
                if debug.DEBUG:
                    print('[DEBUG][1.4]_Пользователь_', docker_username, '_внесен_в_группы_sudo_docker')
                break
    # установка и конфигурация auditd
    call = subprocess.run(["dpkg", "-l"], stdout=subprocess.PIPE, text=True)
    if call.stdout.find('auditd') < 0:
        user_choice = input('Вы хотите использовать auditd для контроля вызовов(Да/Нет)?')
        if user_choice[0] == 'Y' or user_choice[0] == 'y':
            if debug.DEBUG:
                print('[DEBUG][1.6]_Сработало_вхождение_Установка_auditd')
            subprocess.call(["apt", "update"])
            subprocess.call(["apt", "install", "auditd", "-y"])
            if debug.DEBUG:
                print('[DEBUG][1.7]_Вызов_auditd()')
            auditd()
    else:
        print('auditd уже установлен')
        if debug.DEBUG:
            print('[DEBUG][1.6]_Вызов_auditd()')
        auditd()
    # Установка Docker bench security
    choice_username = input('Вы хотите установить docker benchmark(Y/N)?')
    if choice_username[0] == 'Y' or choice_username[0] == 'y':
        if debug.DEBUG:
            print('[DEBUG][1.7]_Сработало_вхождение_начата_скачивание_docker_bench')
        subprocess.call(["git", "clone", "https://github.com/docker/docker-bench-security.git"])
        subprocess.call(["cd", "docker-bench-security"])
        docker_bench_report = subprocess.run(["sh", "docker-bench-security.sh"], stdout=subprocess.PIPE, text=True)
        subprocess.call(["cd", ".."])
        report_file = open("docker_bench_report", "w")
        if debug.DEBUG:
            print("[DEBUG][1.8]_Запись_результатов_в_docker_bench_report")
        report_file.write(docker_bench_report.stdout)
        if debug.DEBUG:
            print("[DEBUG][1.9]_Запись_результатов_завершена")
    if debug.DEBUG:
        print('[DEBUG][1.10]_Выход_docker_preparation')
