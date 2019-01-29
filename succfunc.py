# -*- coding: utf-8 -*-
import sys
import os
from workflow import Workflow3
from workflow.notify import notify


HISTORY_JSON='history.log'
TEMP_JSON='temp_history.log'

wf = Workflow3()


def clean_cahce():
    wf.clear_cache(lambda x: not x.startswith('__'))
    notify('Alfred Dict', 'Clean cache successfully!')


def clean_history():
    if os.path.isfile(HISTORY_JSON):
        os.remove(HISTORY_JSON)
    if os.path.isfile(TEMP_JSON):
        os.remove(TEMP_JSON)
    notify('Alfred Dict','Clean history successfully!')


def succfunc(wf):
    query = sys.argv[1]
    query = query.split('$%')
    part = int(sys.argv[2])

    if part == 0:
        sys.stdout.write(query[0].strip())
    elif part == 1:
        if query[4] == 'cleancache':
            clean_cahce()
        elif query[4] == 'cleanhistory':
            clean_history()
        else:
            sys.stdout.write(query[1].strip())
    elif part == 2:
        if query[2]:
            bashCommand = "say --voice='Samantha' " + query[2]
            os.system(bashCommand)
        if query[3]:
            bashCommand = "say --voice='Ting-Ting' " + query[3]
            os.system(bashCommand)


if __name__ == '__main__':
    sys.exit(wf.run(succfunc))
