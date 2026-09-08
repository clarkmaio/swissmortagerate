import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from plots import plot_curve

matplotlib.use('Agg')


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'Mortage rate rent reference': [0.0125, 0.0150, 0.0175],
            'Average mortage rate': [0.0130, 0.0148, 0.0170],
        },
        index=pd.to_datetime(['2020-03-02', '2023-06-01', '2023-12-01']),
    )


def test_plot_curve_draws_both_lines(sample_df: pd.DataFrame):
    fig, ax = plt.subplots()
    returned_ax = plot_curve(sample_df, ax=ax)

    assert returned_ax is ax
    assert len(ax.lines) == 2

    labels = [line.get_label() for line in ax.lines]
    assert 'Mortage rate rent reference' in labels
    assert 'Average mortage rate' in labels


def test_plot_curve_saves_and_closes_when_save_path_given(sample_df: pd.DataFrame, tmp_path):
    out = tmp_path / 'curve.png'
    ax = plot_curve(sample_df, save_path=str(out))

    assert out.exists()
    assert out.stat().st_size > 0
    assert not plt.fignum_exists(ax.figure.number)


def test_plot_curve_title_and_ylabel(sample_df: pd.DataFrame):
    fig, ax = plt.subplots()
    plot_curve(sample_df, ax=ax)

    assert ax.get_title() == 'Swiss mortage rate'
    assert ax.get_ylabel() == '%'
