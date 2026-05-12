# swissmortagerate
This is just a data scraper of Swiss mortage rate.<br>
Data source is the [federal website](https://www.bwo.admin.ch/bwo/it/home/mietrecht/referenzzinssatz/entwicklung-referenzzinssatz-und-durchschnittszinssatz.html) (**Bundesamt für Wohnungswesen BWO**).

I've written it to prove to my house holder I should receive a rent reduction.

**I made it** :)


<br>

To download and generate the plot just use the simple functions in `data_loader.py`:

```
from data_loader import load_mortagerate, plot_curve

df = load_mortagerate()
plot_curve(df=df)
```

<br><br>
<img src = "https://raw.githubusercontent.com/clarkmaio/SwissMortageRate/main/swiss_mortage_rate.png" style="width:600px;">

<br><br>

## API server

A small FastAPI app (`api.py`) exposes the scraped data over HTTP. It reads `swiss_mortage_rate.parquet` at startup, so make sure the file is present (run `python data_loader.py` first if needed).

Start the server with:

```
uvicorn api:app --reload
```

The server listens on `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

### Endpoints

- `GET /current` — latest reference rate and average mortgage rate.
- `GET /history?valuedate=YYYY-MM-DD` — as-of lookup: the most recent published entry with `valuedate <= input`.

### Examples

Get the most recent rates:

```
curl http://localhost:8000/current
```

Get the rates active on a given date:

```
curl "http://localhost:8000/history?valuedate=2023-06-01"
```

Both endpoints return JSON in the form:

```json
{
  "valuedate": "2023-06-01",
  "mortgage_rate_reference": 0.0150,
  "average_mortgage_rate": 0.0148
}
```

