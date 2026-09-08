from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import yaml

from pipeline import update_dataset


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'Mortage rate rent reference': [0.0150],
            'valid from': pd.to_datetime(['2023-06-01']),
            'Average mortage rate': [0.0148],
        },
        index=pd.to_datetime(['2023-06-01']),
    )


def test_update_dataset_writes_expected_files(sample_df: pd.DataFrame, tmp_path: Path):
    mock_smr = MagicMock()
    mock_smr.data = sample_df
    mock_smr.plot = MagicMock()

    with patch('pipeline.SwissMortageRate', return_value=mock_smr):
        output = update_dataset(output_dir=tmp_path, source_url='http://example.com')

    assert output == tmp_path

    parquet_path = tmp_path / 'swiss_mortage_rate.parquet'
    plot_path = tmp_path / 'swiss_mortage_rate.png'
    metadata_path = tmp_path / 'metadata.yml'

    assert parquet_path.exists()
    assert plot_path.exists()
    assert metadata_path.exists()

    mock_smr.plot.assert_called_once_with(save_path=str(plot_path))

    with open(metadata_path) as f:
        metadata = yaml.safe_load(f)

    assert metadata['source'] == 'http://example.com'
    assert 'rundate' in metadata
    datetime.strptime(metadata['rundate'], '%Y-%m-%d %H:%M:%S')
