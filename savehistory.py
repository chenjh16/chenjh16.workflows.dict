from workflow import Workflow3
from workflow.notify import notify
import json
import time
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')


HISTORY_JSON='history.log'
TEMP_JSON='temp_history.log'


def store(file, data):
    with open(file, 'w') as fw:
        json.dump(data, fw, ensure_ascii=False)


def load(file):
    with open(file,'r') as f:
        data = json.load(f)
        return data


def main(wf):
    if os.path.isfile(TEMP_JSON):
        temp_data = load(TEMP_JSON)
        if 'query' in temp_data.keys():
            query = temp_data['query']
            if os.path.isfile(HISTORY_JSON):
                history_datum = load(HISTORY_JSON)
            else:
                history_datum = {}
            if query in history_datum.keys():
                times = history_datum[query]
            else:
                times = 0
            history_datum[query] = times + 1
            store(HISTORY_JSON, history_datum)


if __name__ == '__main__':
    main("hello")