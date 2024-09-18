# SwissMortageRate
This is just a data scraper of Swiss mortage rate.<br>
Data source is the [federal website](https://www.bwo.admin.ch/bwo/it/home/mietrecht/referenzzinssatz/entwicklung-referenzzinssatz-und-durchschnittszinssatz.html) (**Bundesamt für Wohnungswesen BWO**).

I've written it to prove to my house holder I should receive a rent reduction.

**I made it** :)


<br>

To download and generate the plot just use the simple functions in `data_loader.py`:

```
from data_loader import data_loader, plot_curve

df = data_loader()
plot_curve(df=df)
```

<br><br>
<img src = "https://raw.githubusercontent.com/clarkmaio/SwissMortageRate/main/swiss_mortage_rate.png" style="width:600px;">

