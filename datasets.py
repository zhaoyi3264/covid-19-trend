__headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

def str2num(i):
    if i == 'N/A':
        return None
    if i.endswith('%'):
        i = i[:-1]
    return float(i.replace(',', ''))

def bno():
    '''
    Today's data from BNO `https://bnonews.com/index.php/2020/04/the-latest-coronavirus-cases/`
    '''
    from urllib.request import Request, urlopen
    from bs4 import BeautifulSoup
    import pandas as pd
    
    # scrape data
    req = Request('https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=0&range=A1:I206', headers=__headers)
    with urlopen(req) as res:
        data = res.read().decode('utf-8')

    # parse the html table
    soup = BeautifulSoup(data, 'html.parser')
    tbody = soup.find('html').find('tbody')
    trs = tbody.find_all('tr')
    table = []
    for tr in trs[6:-3]:
        table.append([str(td.string) for td in tr.find_all('td')[:-1]])
    df = pd.DataFrame(table[1:], columns=table[0])
    
    # clean data
    df.set_index('LOCATION', inplace=True)
    today = df.applymap(str2num)
    return today

def pomber():
    '''
    Full timeline data from `https://pomber.github.io/covid19/timeseries.json`
    '''
    from urllib.request import Request, urlopen
    import json
    import numpy as np
    import pandas as pd
    
    # fetch data
    req = Request('https://pomber.github.io/covid19/timeseries.json', headers=__headers)
    with urlopen(req) as res:
        data = json.load(res)

    # concatenate DataFrames
    df = None
    for values in data.values():
        if df is None:
            df = pd.DataFrame(values)
        else:
            df = df.append(pd.DataFrame(values))
    df['date'] = df['date'].apply(pd.to_datetime)
    # add country column
    df['country'] = np.repeat(list(data.keys()), len(data['US']))
    df.rename(columns=str.title, inplace=True)

    # set multi-index, sort, and alter columns
    df.set_index(['Country', 'Date'], inplace=True)
    df.sort_values(['Country', 'Date'], inplace=True)
    df.columns = ['Cases', 'Deaths','Recovered']
    return df

def virus_tracker():
    '''
    Today's data from virus tracker ```https://thevirustracker.com/```
    '''
    from urllib.request import Request, urlopen
    import json
    import pandas as pd

    req = Request('https://api.thevirustracker.com/free-api?countryTotals=ALL', headers=__headers)
    with urlopen(req) as res:
        data = json.load(res)

    items = data['countryitems'][0]
    if 'stat' in items:
        del items['stat']
    df = pd.DataFrame(items).T
    df.drop(columns=['ourid', 'code', 'source'], inplace=True)
    df.rename(columns=lambda name: name.replace('total_', '').title(), inplace=True)
    df.set_index('Title', inplace=True)
    df.index.name = 'Country'
    df = df.applymap(int)
    return df

def jhu():
    '''
    Timeline data from CSSE at Johns Hopkins University `https://github.com/CSSEGISandData/COVID-19`
    '''
    from urllib.request import Request, urlopen
    import pandas as pd
    d = {
    'Cases': 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
    'Deaths': 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
    'Recovered': 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
}
    data = {}
    for key, value in d.items():
        req = Request(value, headers=__headers)
        with urlopen(req) as res:
            df = pd.read_html(res.read())[0].drop(columns=['Unnamed: 0', 'Lat', 'Long']).groupby("Country/Region").sum()
        df.rename(columns=pd.to_datetime, inplace=True)
        ser = df.unstack()
        ser.index.names = ['Date', 'Country']
        ser.name = key
        data[key] = ser
    countries = set(df.index)
    df = pd.DataFrame(data).swaplevel()
    df.sort_values(['Country', 'Date'], inplace=True)
    return df, countries