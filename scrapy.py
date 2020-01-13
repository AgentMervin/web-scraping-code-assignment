import urllib.request
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

new_index = []
wiki = "https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"


def get_date_series():
    dates = pd.date_range(start='1-1-2019', periods=365, tz='UTC')
    df = pd.DataFrame(np.zeros((365,), dtype=int), index=dates, columns=['value'])
    return df


def check_qualification(new_index, table_rows):
    num = len(new_index)
    start, end = new_index[num - 2], new_index[num - 1]
    # print(start)
    for k in range(start, end):
        # print(str(table_rows[i]))
        if orbit_launch(str(table_rows[k])):
            return True

    return False


def orbit_launch(text):
    target_info = ['Successful', 'Operational', 'En Route']
    for target in target_info:
        if re.search(target, text):
            return True

    return False


def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')


def gen_index(text):
    pattern = re.compile(r'\d+\s\w+')
    match = pattern.match(text)
    month_raw = match.group().split(' ')[1][:-2]
    month = month_string_to_number(month_raw)
    day = match.group().split(' ')[0]
    year = '2019'
    iso = ' 00:00:00+00:00'
    return year + '-' + str(month) + '-' + day + ' ' + iso


def get_table(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page)
    right_table = soup.find('table', class_='wikitable collapsible')
    table_rows = right_table.find_all('tr')
    return table_rows


def spider():
    table_rows = get_table(wiki)
    df = get_date_series()
    for i in range(int(len(table_rows))):
        date_text = table_rows[i].find('td')
        if date_text:
            # find all the distinct launches!
            if re.search("\d+\s\w+\d+:\d|\d+\s\w+\[", date_text.text):
                # find the date of launch
                pattern = re.compile(r'\d+\s\w+')
                match = pattern.match(date_text.text)
                new_index.append(i)
                if len(new_index) >= 2:
                    pre_date_text = table_rows[new_index[len(new_index) - 2]].find('td')
                    if check_qualification(new_index, table_rows):
                        print('This launch is qualified!')
                        index = gen_index(pre_date_text.text)
                        df['value'][index] += 1
                    else:
                        print("This launch is unqualified!")
                        new_index.remove(new_index[len(new_index) - 2])

        else:
            print("Tag td is not found!")
    new_index.append(len(table_rows) - 1)
    pre_date_text = table_rows[new_index[len(new_index) - 2]].find('td')
    index = gen_index(pre_date_text.text)
    df['value'][index] += 1
    df.to_csv(r'export_dataframe.csv', index=True, index_label='Date')


if __name__ == '__main__':
    spider()
