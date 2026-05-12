from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from swiss_mortage_rate import SwissMortageRate


class TestInit:
    def test_loads_from_parquet(self, sample_parquet: Path, sample_df: pd.DataFrame):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        pd.testing.assert_frame_equal(smr.data, sample_df)

    def test_default_calls_load_mortagerate(self, sample_df: pd.DataFrame):
        with patch(
            'swiss_mortage_rate.load_mortagerate', return_value=sample_df
        ) as mocked:
            smr = SwissMortageRate()
        mocked.assert_called_once()
        pd.testing.assert_frame_equal(smr.data, sample_df)

    def test_data_is_sorted(self, tmp_path: Path, sample_df: pd.DataFrame):
        shuffled = sample_df.iloc[[2, 0, 3, 1]]
        path = tmp_path / 'shuffled.parquet'
        shuffled.to_parquet(path)

        smr = SwissMortageRate(parquet_path=path)

        assert smr.data.index.is_monotonic_increasing


class TestGetRate:
    def test_exact_match(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_rate('2023-06-01')

        assert result['valuedate'] == pd.Timestamp('2023-06-01')
        assert result['mortgage_rate_reference'] == pytest.approx(0.0150)
        assert result['average_mortgage_rate'] == pytest.approx(0.0148)

    def test_asof_between_published_dates(self, sample_parquet: Path):
        '''A date between two published entries returns the previous entry.'''
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_rate('2023-08-15')

        assert result['valuedate'] == pd.Timestamp('2023-06-01')
        assert result['mortgage_rate_reference'] == pytest.approx(0.0150)

    def test_asof_after_last_entry_returns_last(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_rate('2099-01-01')

        assert result['valuedate'] == pd.Timestamp('2024-06-03')
        assert result['mortgage_rate_reference'] == pytest.approx(0.0150)
        assert result['average_mortgage_rate'] == pytest.approx(0.0155)

    def test_too_old_raises(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        with pytest.raises(ValueError, match='No data available before'):
            smr.get_rate('1999-01-01')

    def test_accepts_datetime_objects(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_rate(pd.Timestamp('2023-12-01'))

        assert result['valuedate'] == pd.Timestamp('2023-12-01')
        assert result['mortgage_rate_reference'] == pytest.approx(0.0175)

    def test_no_argument_returns_current(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_rate()

        assert result['valuedate'] == pd.Timestamp('2024-06-03')
        assert result['mortgage_rate_reference'] == pytest.approx(0.0150)
        assert result['average_mortgage_rate'] == pytest.approx(0.0155)


class TestGetChange:
    def test_change_is_current_minus_from(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_change('2020-03-02')

        assert result['from']['valuedate'] == pd.Timestamp('2020-03-02')
        assert result['from']['mortgage_rate_reference'] == pytest.approx(0.0125)
        assert result['current']['valuedate'] == pd.Timestamp('2024-06-03')
        assert result['current']['mortgage_rate_reference'] == pytest.approx(0.0150)
        assert result['mortgage_rate_change'] == pytest.approx(0.0025)

    def test_change_can_be_negative(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_change('2023-12-01')

        assert result['mortgage_rate_change'] == pytest.approx(-0.0025)

    def test_change_zero_when_from_equals_current(self, sample_parquet: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        result = smr.get_change('2024-06-03')

        assert result['mortgage_rate_change'] == pytest.approx(0.0)


class TestPlot:
    def test_plot_saves_file(self, sample_parquet: Path, tmp_path: Path):
        smr = SwissMortageRate(parquet_path=sample_parquet)
        out = tmp_path / 'curve.png'

        smr.plot(save_path=str(out))

        assert out.exists()
        assert out.stat().st_size > 0
