from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATA_PATH = Path(__file__).parent / 'swiss_mortage_rate.parquet'

app = FastAPI(
    title='Swiss Mortgage Rate API',
    description='Expose Swiss mortgage reference rate and average mortgage rate.',
)


class MortgageRate(BaseModel):
    valuedate: date
    mortgage_rate_reference: float
    average_mortgage_rate: float


def load_data() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)
    df = df.sort_index()
    return df


@app.on_event('startup')
def _startup() -> None:
    app.state.df = load_data()


def _row_to_response(idx: pd.Timestamp, row: pd.Series) -> MortgageRate:
    return MortgageRate(
        valuedate=idx.date(),
        mortgage_rate_reference=float(row['Mortage rate rent reference']),
        average_mortgage_rate=float(row['Average mortage rate']),
    )


@app.get('/current', response_model=MortgageRate)
def current() -> MortgageRate:
    '''Return the most recent mortgage reference rate and average mortgage rate.'''
    df: pd.DataFrame = app.state.df
    idx = df.index.max()
    return _row_to_response(idx, df.loc[idx])


@app.get('/history', response_model=MortgageRate)
def history(valuedate: date) -> MortgageRate:
    '''
    Return the mortgage reference rate and average mortgage rate active on the given date.
    Lookup is "as-of": returns the most recent published entry with valuedate <= input.
    '''
    df: pd.DataFrame = app.state.df
    target = pd.Timestamp(valuedate)

    if target < df.index.min():
        raise HTTPException(
            status_code=404,
            detail=f'No data available before {df.index.min().date().isoformat()}',
        )

    asof = df.index.asof(target)
    return _row_to_response(asof, df.loc[asof])
