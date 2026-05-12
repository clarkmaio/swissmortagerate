import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_df() -> pd.DataFrame:
    '''
    Minimal in-memory dataset mimicking the real schema produced by
    `load_mortagerate`: indexed by `valuedate` (datetime, sorted) with
    columns 'Mortage rate rent reference', 'valid from' and
    'Average mortage rate' (rates stored as fractions).
    '''
    df = pd.DataFrame(
        {
            'Mortage rate rent reference': [0.0125, 0.0150, 0.0175, 0.0150],
            'valid from': pd.to_datetime(
                ['2020-04-01', '2023-06-01', '2023-12-01', '2024-06-01']
            ),
            'Average mortage rate': [0.0130, 0.0148, 0.0170, 0.0155],
        },
        index=pd.to_datetime(
            ['2020-03-02', '2023-06-01', '2023-12-01', '2024-06-03']
        ),
    )
    df.index.name = 'valuedate'
    return df


@pytest.fixture
def sample_parquet(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    path = tmp_path / 'sample.parquet'
    sample_df.to_parquet(path)
    return path
