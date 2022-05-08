import debug
import config


def run_stage(string, dockerfile):
    if debug.DEBUG:
        print('[DEBUG][6.1]_Вызов_run_stage')
    config.RUN_COUNT += 1
    if debug.DEBUG:
        print('[DEBUG][6.2]_Выход_из_run_stage')
