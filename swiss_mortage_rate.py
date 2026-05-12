from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from data_loader import load_mortagerate, plot_curve


DateLike = Union[str, date, datetime, pd.Timestamp]

REFERENCE_COL = 'Mortage rate rent reference'
AVERAGE_COL = 'Average mortage rate'


class SwissMortageRate:
    '''
    Wrapper around the Swiss mortgage rate dataset.

    On instantiation the data is loaded once and cached on the instance. By
    default the data is scraped live from the BWO website via
    `load_mortagerate`; passing `parquet_path` instead reads a previously
    saved parquet file (much faster, useful for tests / API serving).

    Parameters
    ----------
    parquet_path : str or pathlib.Path, optional
        If provided, load the dataset from this parquet file instead of
        scraping the website.
    '''

    def __init__(self, parquet_path: Optional[Union[str, Path]] = None) -> None:
        if parquet_path is not None:
            df = pd.read_parquet(parquet_path)
            df = df.sort_index()
        else:
            df = load_mortagerate()
        self._data = df

    @property
    def data(self) -> pd.DataFrame:
        '''The loaded dataset, indexed by `valuedate`.'''
        return self._data

    def plot(self, save_path: Optional[str] = None) -> None:
        '''Plot the reference and average mortgage rate curves.'''
        plot_curve(self._data, save_path=save_path)

    def get_rate(self, query_date: Optional[DateLike] = None) -> dict:
        '''
        Return the reference and average mortgage rate active on `query_date`.

        If `query_date` is None (the default), the most recent published
        rates are returned via `_current`. Otherwise the lookup is "as-of":
        the most recent published entry with `valuedate <= query_date` is
        returned. Raises `ValueError` if the date is older than the first
        observation in the dataset.

        Returns
        -------
        dict
            {
                'valuedate': pandas.Timestamp,
                'mortgage_rate_reference': float,
                'average_mortgage_rate': float,
            }
        '''
        if query_date is None:
            return self._current()

        idx = self._asof(query_date)
        row = self._data.loc[idx]
        return {
            'valuedate': idx,
            'mortgage_rate_reference': float(row[REFERENCE_COL]),
            'average_mortgage_rate': float(row[AVERAGE_COL]),
        }

    def get_change(self, from_date: DateLike) -> dict:
        '''
        Compare the rates at `from_date` with the most recent published rates.

        The change reported is on the mortgage *reference* rate only
        (absolute difference: current - from). Both endpoint rate snapshots
        are returned so the caller can also derive the change on the average
        rate if needed.

        Returns
        -------
        dict
            {
                'from': {valuedate, mortgage_rate_reference, average_mortgage_rate},
                'current': {valuedate, mortgage_rate_reference, average_mortgage_rate},
                'mortgage_rate_change': float,
            }
        '''
        from_rates = self.get_rate(from_date)
        current_rates = self._current()
        change = (
            current_rates['mortgage_rate_reference']
            - from_rates['mortgage_rate_reference']
        )
        return {
            'from': from_rates,
            'current': current_rates,
            'mortgage_rate_change': change,
        }

    def _current(self) -> dict:
        idx = self._data.index.max()
        row = self._data.loc[idx]
        return {
            'valuedate': idx,
            'mortgage_rate_reference': float(row[REFERENCE_COL]),
            'average_mortgage_rate': float(row[AVERAGE_COL]),
        }

    def _asof(self, query_date: DateLike) -> pd.Timestamp:
        target = pd.Timestamp(query_date)
        if target < self._data.index.min():
            raise ValueError(
                f'No data available before {self._data.index.min().date().isoformat()}'
            )
        return self._data.index.asof(target)
