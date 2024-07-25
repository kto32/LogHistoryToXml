import os.path

import pandas as pd
import polars as pl
from openpyxl.styles.alignment import Alignment
from datetime import datetime

from downable import getHistory

history = []
dopArr = []

def getDownable(minDate, maxDate, type, filename, timed = False):
    global history
    global dopArr
    if len(history) == 0:
        path = './history/'+filename+'.csv'
        if os.path.exists(path):
            history = getHistory(path)
    if len(history) > 0:
        result = (
            history.filter(
                (pl.col('Дата данных') >= datetime.strptime(minDate, '%Y.%m.%d %H:%M:%S'))
                &
                (pl.col('Дата данных') <= datetime.strptime(maxDate, '%Y.%m.%d %H:%M:%S')))
        )
        if timed == False:
            r = result.to_pandas()
            if len(dopArr) > 0:
                dopArr = pd.concat([dopArr, r])
            else:
                dopArr = r

        if type == 'sell':
            if len(result['Макс. цена периода сделки']) > 0:
                maxVal = max(result['Макс. цена периода сделки'])
                r2 = (
                    result.filter(pl.col('Макс. цена периода сделки') == maxVal)
                )
                r3 = {
                    "date": r2["Дата данных"][0],
                    "time": r2["Время данных"][0],
                    "val": r2["Макс. цена периода сделки"][0]
                }
                return r3
        else:
            if len(result['Мин. цена периода сделки']) > 0:
                minVal = min(result['Мин. цена периода сделки'])
                r2 = (
                    result.filter(pl.col('Мин. цена периода сделки') == minVal)
                )
                r3 = {
                    "date": r2["Дата данных"][0],
                    "time": r2["Время данных"][0],
                    "val": r2["Мин. цена периода сделки"][0]
                }
                return r3

    return {
        'date': 0,
        'time': 0,
        'val': 0
    }
    # pass

def create(arr, filename, isFulHistory=False, noHistory=False):
    global dopArr
    data = {
        'Тип данных': [],
        'Дата данных': [],
        'Время данных': [],
        'none-1': [],
        'Ордер на открытие': [],
        'Направление сделки': [],
        'Цена открытия': [],
        'none-2': [],
        'Мин. цена периода сделки': [],
        'Макс. цена периода сделки': [],
        'none-3': [],
        'Ордер на закрытие': [],
        'День закрытия сделки': [],
        'Время закрытия сделки': [],
        'Цена закрытия': [],
        'none-4': [],
        'Длительность сделки': [],
        'Профит, пункты ': [],
        'Просадка, пункты' : [],
        'Цена просадки': [],
        'Дата цены просадки': [],
        'Время цены просадки': []
    }
    for item in arr:
        minDate = item['date-open']  + ' ' + item['time-open']
        maxDate = item['date-close'] + ' ' + item['time-close']
        downableArr = getDownable(minDate, maxDate, item['type'], filename, isFulHistory or noHistory)
        resultPunkt = float(item['price-open']) - float(downableArr['val'])
        minV = ''
        maxV = ''
        if item['type'] == 'buy':
            resultPunkt = resultPunkt * -1
            minV = downableArr['val']
        else:
            maxV = downableArr['val']

        data['Тип данных'].append('Сделка')
        data['Дата данных'].append(item['date-open']  + ' ' + item['time-open'])
        data['Время данных'].append(item['time-open'])
        data['none-1'].append(' ')
        data['Ордер на открытие'].append(int(item['id']))
        data['Направление сделки'].append(item['type'])
        data['Цена открытия'].append(float(item['price-open']))
        data['none-2'].append(' ')
        data['Мин. цена периода сделки'].append(minV)
        data['Макс. цена периода сделки'].append(maxV)
        data['none-3'].append(' ')
        data['Ордер на закрытие'].append(int(item['id-close']))
        data['День закрытия сделки'].append(item['date-close'] + ' ' + item['time-close'])
        data['Время закрытия сделки'].append(item['time-close'])
        data['Цена закрытия'].append(float(item['price-close']))
        data['none-4'].append(' ')
        data['Длительность сделки'].append(item['difference-date'])
        data['Профит, пункты '].append(float(item['profit']))
        data['Просадка, пункты'].append(resultPunkt)
        data['Цена просадки'].append(downableArr['val'])
        data['Дата цены просадки'].append(downableArr['date'])
        data['Время цены просадки'].append(downableArr['time'])

    data = pd.DataFrame(data)

    if len(dopArr) > 0:
        data = pd.concat([data, dopArr])

    if isFulHistory:
        global history
        if len(history) > 0:
            r = history.to_pandas()
            data = pd.concat([data, r])

    # del dopArr
    # del history

    data['Дата данных'] = pd.to_datetime(data['Дата данных'])
    data['День закрытия сделки'] = pd.to_datetime(data['День закрытия сделки'])

    # print(data.columns[data.columns.duplicated(keep=False)])
    data.reset_index(inplace=True, drop=True)
    # data = (
    #     data.style
    #         .map(lambda x: 'text-align: center')
    #         .map(lambda x: 'number-format: yyyy.mm.dd', subset=['Дата данных', 'Дата цены просадки', 'День закрытия сделки'])
    #         .map(lambda x: 'number-format: h:mm:ss', subset=['Время данных', 'Время закрытия сделки', 'Длительность сделки', 'Время цены просадки'])
    #         .map(lambda x: 'number-format: 0.00000', subset=[
    #         'Цена открытия', 'Мин. цена периода сделки', 'Макс. цена периода сделки',
    #         'Цена закрытия', 'Профит, пункты ', 'Цена просадки', 'Просадка, пункты'])
    # )
    # data.style.apply(lambda x: 'number-format: yyyy.mm.dd', axis=1, subset=['Дата данных'])
    # data = data.style.apply(lambda x: pd.Series('text-align: center'),axis=0, subset='A')

    print('Начало записи')
    with (pd.ExcelWriter('./xmls/'+filename+'.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer):
        data.style\
            .map(lambda x: 'text-align: center')\
            .map(lambda x: 'border-right: 6px solid black', subset=['Время данных'])\
            .map(lambda x: 'number-format: yyyy.mm.dd', subset=['Дата данных', 'Дата цены просадки', 'День закрытия сделки'])\
            .map(lambda x: 'number-format: h:mm:ss', subset=['Время данных', 'Время закрытия сделки', 'Длительность сделки', 'Время цены просадки'])\
            .map(lambda x: 'number-format: 0.00000', subset=[
            'Цена открытия', 'Мин. цена периода сделки', 'Макс. цена периода сделки',
            'Цена закрытия', 'Профит, пункты ', 'Цена просадки', 'Просадка, пункты'])\
            .to_excel(writer, sheet_name='Sheet1', startrow=2, startcol=0, header=False, index=False)
        # del data
        # worksheet = writer.sheets['Sheet1']
        print('Конец записи')
        # print('Начало модификации')
        # for row in worksheet.iter_rows():
        #     for cell in row:
        #         if cell.row < 2:
        #             continue
        #         if(cell.column_letter not in ['B', 'C', 'M', 'U', 'N', 'Q', 'V', 'R', 'S', 'T', 'I', 'J']):
        #             continue
        #
        #         cell.alignment = Alignment(horizontal="center")
        #         if (cell.column_letter == 'B' or cell.column_letter == 'M' or cell.column_letter == 'U'):
        #             worksheet[cell.coordinate].number_format = "yyyy.mm.dd"
        #         if (cell.column_letter == 'C' or cell.column_letter == 'N' or cell.column_letter == 'Q' or cell.column_letter == 'V'):
        #             worksheet[cell.coordinate].number_format = "h:mm:ss"
        #         if (cell.column_letter == 'R'
        #             or cell.column_letter == 'S'
        #             or cell.column_letter == 'T'
        #             or cell.column_letter == 'I'
        #             or cell.column_letter == 'J'):
        #             worksheet[cell.coordinate].number_format = '0.00000'
        # print('Конец модификации')
    # del data