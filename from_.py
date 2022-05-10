import debug
import subprocess
import json
from os import path


# Этап проверки образа для инструкции FROM из Dockerfile
def from_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][2.1]_Вызов_from_stage')
    # Работа со строкой
    docker_image = string[1]
    docker_image = docker_image.replace('\n', '')
    if debug.DEBUG:
        print('[DEBUG][2.2]', docker_image)
    # Проверка наличия snyk
    if not path.exists("snyk"):
        if debug.DEBUG:
            print('[DEBUG][2.3]_Сработало_вхождение_snyk_отсутствует_в_текущей_директории')
        # Скачивание snyk для linux - инструмент для анализа завимимостей
        subprocess.call(["curl", "https://static.snyk.io/cli/latest/snyk-linux", "-o", "snyk"])
    subprocess.call(["chmod", "+x", "./snyk"])
    # Для работы необходима регистрация в snyk
    subprocess.call(["./snyk", "auth"])
    call_container_test = subprocess.run(["./snyk", "container", "test", docker_image,
                                          "--severity-threshold=high", "--json"], stdout=subprocess.PIPE, text=True)
    data = json.loads(call_container_test.stdout)
    if data.get('summary') == 'No high or critical severity vulnerabilities':
        if debug.DEBUG:
            print('[DEBUG][2.4]_Сработало_вхождение_отсутствуют_уязвимости_высокой_серьезности')
        print(docker_image, 'проверен и получен из надежного источника')
        # Запись в новый Dockerfile: FROM + старый образ
        dockerfile.write(f'FROM {docker_image}\n')
    else:
        if debug.DEBUG:
            print('[DEBUG][2.5]_Сработало_вхождение_присутствуют_уязвимости_высокой_серьезности')
            print('[DEBUG][2.6]_Или_получена_ошибка')
        # Формирование отчета по уязвимостям
        report = open('report_' + docker_image, "a")
        report.write(json.dumps(data))
        report.close()
        # Формирование образа на замену уязвимому
        buffer_message = ''
        counter = 1
        # Поиск рекомендуемого образа на замену в json файле
        for item in data['docker']['baseImageRemediation']['advice']:
            if counter == 0:
                buffer_message = item['message']
            if item['message'] == 'Major upgrades':
                counter = 0
        second_buffer = buffer_message.split('\n')
        third_buffer = second_buffer[1].split(' ')
        recommended_image = third_buffer[0]
        if debug.DEBUG:
            print('[DEBUG][2.7]_recommended_image-', recommended_image)
        # Запись в новый Dockerfile: FROM + новый образ
        dockerfile.write(f'FROM {recommended_image}\n')
    if debug.DEBUG:
        print('[DEBUG][2.8]_Выход_из_from_stage')
