from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from swiss_mortage_rate import SwissMortageRate

DATA_PATH = Path(__file__).parent / 'swiss_mortage_rate.parquet'

app = FastAPI(
    title='Swiss Mortgage Rate API',
    description='Expose Swiss mortgage reference rate and average mortgage rate.',
)


class MortgageRate(BaseModel):
    valuedate: date
    mortgage_rate_reference: float
    average_mortgage_rate: float


@app.on_event('startup')
def _startup() -> None:
    app.state.smr = SwissMortageRate(parquet_path=DATA_PATH)


@app.get('/current', response_model=MortgageRate)
def current() -> MortgageRate:
    '''Return the most recent mortgage reference rate and average mortgage rate.'''
    rate = app.state.smr.get_rate()
    return MortgageRate(
        valuedate=rate['valuedate'].date(),
        mortgage_rate_reference=rate['mortgage_rate_reference'],
        average_mortgage_rate=rate['average_mortgage_rate'],
    )


@app.get('/history', response_model=MortgageRate)
def history(valuedate: date) -> MortgageRate:
    '''
    Return the mortgage reference rate and average mortgage rate active on the given date.
    Lookup is "as-of": returns the most recent published entry with valuedate <= input.
    '''
    try:
        rate = app.state.smr.get_rate(valuedate)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return MortgageRate(
        valuedate=rate['valuedate'].date(),
        mortgage_rate_reference=rate['mortgage_rate_reference'],
        average_mortgage_rate=rate['average_mortgage_rate'],
    )
