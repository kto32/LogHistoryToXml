import polars as pl

def getHistory(path):
    history = (
        pl.scan_csv(path, separator='\t', null_values="0", low_memory=True)
        .with_columns(timestamp=pl.concat_str(pl.col('<DATE>'), pl.col('<TIME>'), separator=' '))
        .with_columns(pl.col('timestamp').str.to_datetime('%Y.%m.%d %H:%M:%S%.f', time_unit='ns'))
        .with_columns(
            type=pl.col('<DATE>').str.replace('(.*)', 'Цена'),
            p1=pl.col('<DATE>').str.replace('(.*)', ''),
            p2=pl.col('<DATE>').str.replace('(.*)', ''),
            p3=pl.col('<DATE>').str.replace('(.*)', ''),
            p4=pl.col('<DATE>').str.replace('(.*)', ''),
            p5=pl.col('<DATE>').str.replace('(.*)', ''),
            p6=pl.col('<DATE>').str.replace('(.*)', ''),
            p7=pl.col('<DATE>').str.replace('(.*)', ''),
            p8=pl.col('<DATE>').str.replace('(.*)', ''),
            p9=pl.col('<DATE>').str.replace('(.*)', ''),
            p10=pl.col('<DATE>').str.replace('(.*)', ''),
            p11=pl.col('<DATE>').str.replace('(.*)', ''),
            p12=pl.col('<DATE>').str.replace('(.*)', ''),
            p13=pl.col('<DATE>').str.replace('(.*)', ''),
            p14=pl.col('<DATE>').str.replace('(.*)', ''),
            p15=pl.col('<DATE>').str.replace('(.*)', ''),
            p16=pl.col('<DATE>').str.replace('(.*)', ''),
            p17=pl.col('<DATE>').str.replace('(.*)', ''),
        )
        .rename({
            'type': 'Тип данных',
            'timestamp': 'Дата данных',
            '<TIME>': 'Время данных',
            'p1': 'none-1',
            'p2': 'Ордер на открытие',
            'p3': 'Направление сделки',
            'p4': 'Цена открытия',
            'p5': 'none-2',
            '<LOW>': 'Мин. цена периода сделки',
            '<HIGH>': 'Макс. цена периода сделки',
            'p6': 'none-3',
            'p7': 'Ордер на закрытие',
            'p8': 'День закрытия сделки',
            'p9': 'Время закрытия сделки',
            'p10': 'Цена закрытия',
            'p11': 'none-4',
            'p12': 'Длительность сделки',
            'p13': 'Профит, пункты ',
            'p14': 'Просадка, пункты',
            'p15': 'Цена просадки',
            'p16': 'Дата цены просадки',
            'p17': 'Время цены просадки',
        })
        # .filter((pl.col('timestamp') >= min) & (pl.col('timestamp') <= max))
        .select(
            'Дата данных',
            'Тип данных',
            'Время данных',
            'none-1',
            'Ордер на открытие',
            'Направление сделки',
            'Цена открытия',
            'none-2',
            'Мин. цена периода сделки',
            'Макс. цена периода сделки',
            'none-3',
            'Ордер на закрытие',
            'День закрытия сделки',
            'Время закрытия сделки',
            'Цена закрытия',
            'none-4',
            'Длительность сделки',
            'Профит, пункты ',
            'Просадка, пункты',
            'Цена просадки',
            'Дата цены просадки',
            'Время цены просадки',
        )
        # .select('timestamp', '<HIGH>', '<LOW>')
        .collect(streaming=True)
    )

    return history