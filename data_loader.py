import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pimpmyplot as pmp
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
    Scrape the Swiss mortgage rate table from the official BWO website and return
    it as a pandas DataFrame.

    The target page renders the table via JavaScript, so a plain `requests` +
    BeautifulSoup approach is not sufficient. A headless Chrome browser is
    started via Selenium to execute the page scripts; once the `<table>` tag is
    present in the DOM (waited for up to 15 seconds), the rendered HTML is
    handed off to BeautifulSoup for parsing.

    The raw cells are then cleaned and typed by `parse_table` / `columns_format`:
        - date columns ('valid from', 'valuedate') are parsed as datetimes
          using the `dd.mm.yyyy` format used on the page;
        - rate columns ('Mortage rate rent reference', 'Average mortage rate')
          are stripped of `%`, `*` and whitespace, comma decimal separators are
          converted to dots, and the values are divided by 100 so the result is
          a fraction (e.g. `1.50%` -> `0.015`).

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by `valuedate` (datetime, sorted ascending) with
        columns:
            - 'Mortage rate rent reference' (float, fraction)
            - 'valid from'                  (datetime)
            - 'Average mortage rate'        (float, fraction)

    Raises
    ------
    RuntimeError
        If the table does not appear on the page within the timeout, or if no
        `<table>` element can be found in the rendered HTML.
    '''

    driver = setup_webdriver()
    driver.get(URL)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
    except Exception:
        driver.quit()
        raise RuntimeError('Timed out waiting for table to load on page')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find('table')
    if table is None:
        raise RuntimeError('Could not find table in page source')

    df = parse_table(table)
    return df




def plot_curve(df: pd.DataFrame, save_path: str = None) -> None:
    '''
    Plot the Swiss mortgage rate reference and the average mortgage rate as
    two time series on the same axes.

    The two rate columns are expected to be stored as fractions (e.g. `0.015`
    for 1.5%) and are multiplied by 100 internally so the y-axis is in
    percentage points. The DataFrame index is used as the x-axis and is
    expected to be the `valuedate` (datetime).

    Styling:
        - 'Mortage rate rent reference' is drawn in red
        - 'Average mortage rate'        is drawn in black
        - dotted grid, bold axis labels, legend, title 'Swiss mortage rate'

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain the columns 'Mortage rate rent reference' and
        'Average mortage rate'. Typically the output of `load_mortagerate`.
    save_path : str, optional
        If provided (and not NaN/None), the figure is written to this path with
        `plt.savefig` and the figure is closed. If omitted, the figure is left
        open so the caller can `plt.show()` it or continue customizing it.

    Returns
    -------
    None
    '''

    df_plot = df[['Mortage rate rent reference', 'Average mortage rate']] * 100

    plt.plot(df_plot.index, df_plot['Mortage rate rent reference'], color='red', label='Mortage rate rent reference')
    plt.plot(df_plot.index, df_plot['Average mortage rate'], color='black', label='Average mortage rate')
    
    pmp.legend()  
    pmp.remove_axis('top', 'right')  

    plt.title('Swiss mortage rate', fontweight='bold')
    plt.ylabel('%', fontweight='bold')
    plt.tight_layout()
    
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
    
