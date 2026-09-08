from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import yaml

from scraper import URL
from swiss_mortage_rate import SwissMortageRate


def update_dataset(
    output_dir: Union[str, Path] = '.',
    parquet_name: str = 'swiss_mortage_rate.parquet',
    plot_name: str = 'swiss_mortage_rate.png',
    metadata_name: str = 'metadata.yml',
    source_url: Optional[str] = None,
) -> Path:
    '''
    Fetch the latest Swiss mortgage rate data and write the parquet, plot, and
    metadata files to `output_dir`.

    Returns
    -------
    pathlib.Path
        The output directory.
    '''
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    smr = SwissMortageRate()

    parquet_path = output_dir / parquet_name
    plot_path = output_dir / plot_name
    metadata_path = output_dir / metadata_name

    smr.data.to_parquet(parquet_path)
    smr.plot(path=str(plot_path))

    metadata = {
        'rundate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': source_url if source_url is not None else URL,
    }

    with open(metadata_path, 'w') as f:
        yaml.dump(metadata, f)

    return output_dir
