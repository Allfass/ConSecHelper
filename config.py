# Блок глобальных переменных для передачи значений из функций, вызываемых primer,
# в параметры запуска контейнеров

# Переменная, для передачи номера порта, в параметры запуска контейнера
EXPOSE_PARAMETER = []
# Счетчики инструкции
ONBUILD_COUNT = 0
RUN_COUNT = 0
USER_COUNT = 0
