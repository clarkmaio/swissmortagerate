import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

LINK = 'https://www.bwo.admin.ch/bwo/it/home/mietrecht/referenzzinssatz/entwicklung-referenzzinssatz-und-durchschnittszinssatz.html'



def data_loader():

    page = requests.get(LINK)
    soup = BeautifulSoup(page.text, 'lxml')
    table = soup.find('table')

    headers = []
    for i in table.find_all('th'):
        title = i.text
        headers.append(title)

    headers = ['Mortage rate rent reference', 'valid from', 'Average mortage rate', 'valuedate']

    df = pd.DataFrame(columns=headers)
    for j in table.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data if i.text != '\xa0']

        if len(row) != 4:
            print(f'Wrong format {row}. Skip row...')
            continue

        length = len(df)
        df.loc[length] = row

    df = columns_format(df)
    df.set_index('valuedate', inplace=True)
    df.sort_index(inplace=True)

    return df


def columns_format(df: pd.DataFrame) -> pd.DataFrame:

    # Format data
    df['valid from'] = [pd.to_datetime(d.replace(' ', ''), format='%d.%m.%Y') for d in df['valid from']]
    df['valuedate'] = [pd.to_datetime(d.replace(' ', ''), format='%d.%m.%Y') for d in df['valuedate']]

    # Format value
    df['Mortage rate rent reference'] = [ float(x.replace(' ','').replace('*', '').replace('%', '').replace(',', '.'))/100 for x in df['Mortage rate rent reference']]
    df['Average mortage rate'] = [float(x.replace(' ', '').replace('*', '').replace('%', '').replace(',', '.')) / 100 for x in df['Average mortage rate']]
    return df


def plot_curve(df: pd.DataFrame, save_path: str = None) -> None:
    '''Simple plot to visualize curves'''
    df_plot = df[['Mortage rate rent reference', 'Average mortage rate']] * 100

    plt.plot(df_plot.index, df_plot['Mortage rate rent reference'], color='red', label='Mortage rate rent reference')
    plt.plot(df_plot.index, df_plot['Average mortage rate'], color='black', label='Average mortage rate')
    plt.grid(linestyle=':')
    plt.legend()
    plt.title('Swiss mortage rate', fontweight='bold')
    plt.xlabel('date', fontweight='bold')
    plt.ylabel('%', fontweight='bold')
    plt.grid(linestyle=':')
    
    
    if not pd.isnull(save_path):
        plt.savefig(save_path)
        plt.close()
    

if __name__ == '__main__':

    df = data_loader()
    plot_curve(df=df)
    
