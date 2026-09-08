import pandas as pd
import pytest

from scraper import HEADERS, parse_bwo_html, parse_table


SAMPLE_HTML = '''
<html>
<body>
<table>
  <tr><th>Referenzzinssatz</th><th>gültig ab</th><th>Durchschnittszinssatz</th><th>Datum</th></tr>
  <tr><td>1,50 %*</td><td>01.06.2023</td><td>1,48 %</td><td>01.06.2023</td></tr>
  <tr><td>1,75 %*</td><td>01.12.2023</td><td>1,70 %</td><td>01.12.2023</td></tr>
  <tr><td>   </td><td></td><td></td><td></td></tr>
</table>
</body>
</html>
'''


def test_parse_bwo_html_returns_expected_dataframe():
    df = parse_bwo_html(SAMPLE_HTML)

    assert list(df.columns) == HEADERS
    assert len(df) == 2
    assert df.index.name == 'valuedate'
    assert df.index.is_monotonic_increasing

    assert df.index[0] == pd.Timestamp('2023-06-01')
    assert df.loc['2023-06-01', 'Mortage rate rent reference'] == pytest.approx(0.015)
    assert df.loc['2023-06-01', 'Average mortage rate'] == pytest.approx(0.0148)
    assert df.loc['2023-06-01', 'valid from'] == pd.Timestamp('2023-06-01')

    assert df.loc['2023-12-01', 'Mortage rate rent reference'] == pytest.approx(0.0175)
    assert df.loc['2023-12-01', 'Average mortage rate'] == pytest.approx(0.017)


def test_parse_bwo_html_raises_when_no_table():
    with pytest.raises(RuntimeError, match='Could not find table'):
        parse_bwo_html('<html></html>')


def test_parse_table_skips_wrong_format_rows():
    from bs4 import BeautifulSoup

    html = '''
    <table>
      <tr><th>Header</th></tr>
      <tr><td>1,50 %*</td><td>01.06.2023</td><td>1,48 %</td><td>01.06.2023</td></tr>
      <tr><td>only</td><td>two</td></tr>
      <tr><td>1,75 %*</td><td>01.12.2023</td><td>1,70 %</td><td>01.12.2023</td></tr>
    </table>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    df = parse_table(soup.find('table'))

    assert len(df) == 2
    assert df.index[-1] == pd.Timestamp('2023-12-01')
