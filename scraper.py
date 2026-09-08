from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

URL = 'https://www.bwo.admin.ch/de/entwicklung-referenzzinssatz-und-durchschnittszinssatz'
HEADERS = ['Mortage rate rent reference', 'valid from', 'Average mortage rate', 'valuedate']


def setup_webdriver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    return driver


def _clean_rates(series: pd.Series) -> pd.Series:
    return series.str.replace(' ', '', regex=False).str.replace('*', '', regex=False).str.replace('%', '', regex=False).str.replace(',', '.', regex=False).astype(float) / 100


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['valid from'] = pd.to_datetime(df['valid from'].str.replace(' ', '', regex=False), format='%d.%m.%Y')
    df['valuedate'] = pd.to_datetime(df['valuedate'].str.replace(' ', '', regex=False), format='%d.%m.%Y')

    df['Mortage rate rent reference'] = _clean_rates(df['Mortage rate rent reference'])
    df['Average mortage rate'] = _clean_rates(df['Average mortage rate'])
    return df


def parse_table(table) -> pd.DataFrame:
    '''
    Extract data from an HTML table and return a pandas DataFrame.
    '''
    df = pd.DataFrame(columns=HEADERS)

    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        values = [cell.text for cell in cells if cell.text != '\xa0']

        if len(values) != 4:
            print(f'Wrong format {values}. Skip row...')
            continue

        df.loc[len(df)] = values

    df = _clean_dataframe(df)
    df.set_index('valuedate', inplace=True)
    df.sort_index(inplace=True)
    return df


def parse_bwo_html(html: str) -> pd.DataFrame:
    '''
    Parse the BWO mortgage-rate HTML and return a cleaned DataFrame.

    This function is separate from `load_mortagerate` so the parsing logic can
    be unit-tested without starting a browser.
    '''
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if table is None:
        raise RuntimeError('Could not find table in page source')
    return parse_table(table)


def load_mortagerate(url: Optional[str] = None, timeout: int = 15) -> pd.DataFrame:
    '''
    Scrape the Swiss mortgage rate table from the official BWO website and
    return it as a pandas DataFrame.

    Parameters
    ----------
    url : str, optional
        URL to scrape. Defaults to `URL`.
    timeout : int, optional
        Seconds to wait for the table to appear in the DOM.

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
    target_url = url if url is not None else URL
    driver = setup_webdriver()
    driver.get(target_url)

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
    except Exception:
        driver.quit()
        raise RuntimeError('Timed out waiting for table to load on page')

    html = driver.page_source
    driver.quit()

    return parse_bwo_html(html)
