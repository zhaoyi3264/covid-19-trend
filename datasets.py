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
    No time line
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
    df.set_index('WORLD', inplace=True)
    today = df.applymap(str2num)
    return today

def pomber():
    '''
    Full timeline data from `https://pomber.github.io/covid19/timeseries.json`
    '''
    from urllib.request import Request, urlopen
    from bs4 import BeautifulSoup
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

    # add country column
    df['country'] = np.repeat(list(data.keys()), len(data['US']))
    df.rename(columns=str.title, inplace=True)
    
    # set multi-index, sort, and alter columns
    df.set_index(['Country', 'Date'], inplace=True)
    df.sort_values(['Country', 'Date'], inplace=True)
    df.columns = ['Cases', 'Deaths','Recovered']
    return df