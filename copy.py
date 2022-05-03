# Функция копирует инструкцию в новый dockerfile
# Используется для инструкций, автоматическая обработка которых - затруднительна или невозможна
def copy_stage(string, dockerfile):
    dockerfile.write(string[0], ' ', string[1])
