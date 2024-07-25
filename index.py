import os
import re
import resource
import time
from datetime import datetime
from shutil import copy
from customXml import create

arr = []
idClose = None


def getDate(string=None):
    if string:
        date = datetime.strptime(string, '%Y.%m.%d %H:%M:%S')
        time = date.strftime('%H:%M:%S')
        date = date.strftime('%Y.%m.%d')
        return {
            'time': time,
            'date': date
        }
    else:
        return {
            'time': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%Y.%m.%d')
        }


def getCreateInfo(string=None):
    info = re.search(r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*#(\d*)\s(\w*)\s.*\sat\s(.*)\sdone', string)
    groups = info.groups()
    dateInfo = getDate(groups[0])
    return {
        'id': groups[1],
        'id-close': 0,
        'type': groups[2],
        'price-open': groups[3],
        'date-open': dateInfo['date'],
        'time-open': dateInfo['time'],
        'date-close': '',
        'time-close': '',
        'price-close': 0,
        'difference-date': '',
        'profit': 0,
    }


def getCloseInfo(string=None, isStopLoss=False, isClosedEndTest=False):
    global arr
    global idClose
    pattern = r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*instant\s.*at\s(.*),.*close\s#(\d*).*'
    if isStopLoss:
        pattern = r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*stop\sloss\striggered\s#(\d*).*\[#(\d*).*at\s(.*)\].*'
    if isClosedEndTest:
        pattern = r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*end\sof\stest\sat\s(.*).*\[#(\d*).*'
    info = re.search(pattern, string)
    groups = info.groups()

    arrVal = {
        'id': groups[2],
        'date': groups[0],
        'price': groups[1],
        'id-close': 0
    }
    if isStopLoss:
        arrVal = {
            'id': groups[1],
            'id-close': groups[2],
            'date': groups[0],
            'price': groups[3]
        }
    else:
        if isClosedEndTest:
            arrVal = {
                'id': groups[2],
                'date': groups[0],
                'price': groups[1],
                'id-close': groups[2]
            }
        else:
            idClose = groups[2]

    arr = list(map(lambda item: update(item, arrVal), arr))


def update(item, groups):
    if item['id'] == groups['id']:
        dateInfo = getDate(groups['date'])
        item['date-close'] = dateInfo['date']
        item['time-close'] = dateInfo['time']
        item['price-close'] = groups['price']
        item['id-close'] = groups['id-close']
        item['difference-date'] = getDifference(item)

        if item['type'] == 'buy':
            item['profit'] = float(item['price-close']) - float(item['price-open'])
        else:
            item['profit'] = float(item['price-open']) - float(item['price-close'])
    return item


def updateIdClose(item, id):
    global idClose
    if item['id'] == idClose:
        item['id-close'] = id

    return item


def getDifference(item):
    dateOpen = datetime.strptime(item['date-open'] + ' ' + item['time-open'], '%Y.%m.%d %H:%M:%S')
    dateCloe = datetime.strptime(item['date-close'] + ' ' + item['time-close'], '%Y.%m.%d %H:%M:%S')
    diff = dateCloe - dateOpen
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def main(isFulHistory=False, noHistory=False):
    global arr
    global idClose
    path = './logs/'
    pathTemplate = './templates/'
    templateName = 'default.xlsx'
    boolCreate = False

    for filename in os.listdir(path):
        if filename != '.DS_Store':
            print('Начало парсинга '+filename)
            with open(path + filename, 'r', encoding='UTF-16 LE') as file:
                while line := file.readline():
                    string = line.rstrip()
                    # result = re.search(r'Trade\s(.*)instant', string)
                    match = re.search(r'Trade\s(.*)instant\s(.*)', string)
                    matchStopLoss = re.search(r'Trade\s(.*)stop loss triggered\s(.*)', string)
                    matchStopTest = re.search(r'Trade\s(.*)position closed due end of test\s(.*)', string)
                    if match:
                        matchClose = re.search(r'Trade\s(.*)instant\s(.*)close', string)
                        if (matchClose):
                            boolCreate = False
                            getCloseInfo(string)
                        else:
                            boolCreate = True

                    if matchStopLoss:
                        boolCreate = False
                        getCloseInfo(string, True)

                    if matchStopTest:
                        boolCreate = False
                        getCloseInfo(string, False, True)

                    if boolCreate or idClose:
                        matchOpen = re.search(r'Trades\s(.*)deal #(\d*)', string)
                        if (matchOpen):
                            if idClose == None:
                                boolCreate = False
                                arr.append(getCreateInfo(string))
                            else:
                                groups = matchOpen.groups()
                                arr = list(map(lambda item: updateIdClose(item, groups[1]), arr))
                                idClose = None

            print('Конец парсинга '+filename)
            if (len(arr) > 0):
                name = filename.split('.')[0]
                copy(pathTemplate + templateName, './xmls/'+name+'.xlsx')
                createXml(name, isFulHistory, noHistory)
                arr = []


def createXml(filename=None, isFulHistory=False, noHistory=False):
    global arr

    create(arr, filename, isFulHistory, noHistory)

    del arr

if __name__ == "__main__":
    print('Доступные режимы:')
    print('1: История сделок')
    print('2: Полная история')
    print('3: Без истории (только просчитанные значения для седлок)')
    print('0: Выход')
    print('Сделайте выбор указав номер и нажав enter')
    while True:
        selected = int(input())
        if selected == 1:
            time_start = time.perf_counter()
            main()
            time_elapsed = (time.perf_counter() - time_start)
            memMb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
            print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))
            break;

        if selected == 2:
            time_start = time.perf_counter()
            main(True)
            time_elapsed = (time.perf_counter() - time_start)
            memMb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
            print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))
            break

        if selected == 3:
            time_start = time.perf_counter()
            main(False, True)
            time_elapsed = (time.perf_counter() - time_start)
            memMb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
            print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))
            break

        if selected == 0:
            break;
