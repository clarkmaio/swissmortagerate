import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

URL = 'https://www.bwo.admin.ch/de/entwicklung-referenzzinssatz-und-durchschnittszinssatz'
HEADERS = ['Mortage rate rent reference', 'valid from', 'Average mortage rate', 'valuedate']


def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def columns_format(df: pd.DataFrame) -> pd.DataFrame:

    # Format data
    df['valid from'] = [pd.to_datetime(d.replace(' ', ''), format='%d.%m.%Y') for d in df['valid from']]
    df['valuedate'] = [pd.to_datetime(d.replace(' ', ''), format='%d.%m.%Y') for d in df['valuedate']]

    # Format value
    df['Mortage rate rent reference'] = [ float(x.replace(' ','').replace('*', '').replace('%', '').replace(',', '.'))/100 for x in df['Mortage rate rent reference']]
    df['Average mortage rate'] = [float(x.replace(' ', '').replace('*', '').replace('%', '').replace(',', '.')) / 100 for x in df['Average mortage rate']]
    return df



def parse_table(table) -> pd.DataFrame:
    '''
    Extract data from html table and return a pandas dataframe
    '''

    df = pd.DataFrame(columns=HEADERS)

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


def load_mortagerate():
    '''
    Scrape data from offical website and return pandas dataframe.
    Note: BS not enough since javascript is used to render the table. Using selenium to load the page.
    '''

    driver = setup_webdriver()
    driver.get(URL)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table')
    driver.quit()

    df = parse_table(table)
    return df




def plot_curve(df: pd.DataFrame, save_path: str = None) -> None:
    '''
    Simple plot to visualize curves
    df must contain columns 'Mortage rate rent reference' and 'Average mortage rate'
    save_path: if not None, save the plot to the given path
    '''

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

    df = load_mortagerate()



    # Save output
    plot_curve(df=df, save_path = './swiss_mortage_rate.png')
    df.to_parquet('./swiss_mortage_rate.parquet')
    
    metadata = {
        'rundate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': URL,
    }

    with open('./metadata.yml', 'w') as f:
        yaml.dump(metadata, f)
    
