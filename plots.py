from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import pimpmyplot as pmp
from matplotlib.axes import Axes

REFERENCE_COL = 'Mortage rate rent reference'
AVERAGE_COL = 'Average mortage rate'


def plot_curve(
    df: pd.DataFrame,
    ax: Optional[Axes] = None,
    path: Optional[str] = None,
) -> Axes:
    '''
    Plot the Swiss mortgage rate reference and the average mortgage rate as
    two time series on the same axes.

    The two rate columns are expected to be stored as fractions (e.g. `0.015`
    for 1.5%) and are multiplied by 100 internally so the y-axis is in
    percentage points. The DataFrame index is used as the x-axis and is
    expected to be the `valuedate` (datetime).

    Styling:
        - 'Mortage rate rent reference' is drawn in red
        - 'Average mortage rate'        is drawn in black
        - dotted grid, bold axis labels, legend, title 'Swiss mortage rate'

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain the columns 'Mortage rate rent reference' and
        'Average mortage rate'.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on. If omitted, a new figure and axes are created.
    path : str, optional
        If provided (and not NaN/None), the figure is written to this path with
        `plt.savefig` and the figure is closed.

    Returns
    -------
    matplotlib.axes.Axes
        The axes the curves were drawn on.
    '''
    if ax is None:
        fig, ax = plt.subplots()

    df_plot = df[[REFERENCE_COL, AVERAGE_COL]] * 100

    ax.plot(
        df_plot.index,
        df_plot[REFERENCE_COL],
        color='red',
        label='Mortage rate rent reference',
    )
    ax.plot(
        df_plot.index,
        df_plot[AVERAGE_COL],
        color='black',
        label='Average mortage rate',
    )

    pmp.legend(ax=ax)
    pmp.remove_axis('top', 'right', ax=ax)

    ax.set_title('Swiss mortage rate', fontweight='bold')
    ax.set_ylabel('%', fontweight='bold')
    ax.figure.tight_layout()

    if path is not None and not pd.isnull(path):
        ax.figure.savefig(path)
        plt.close(ax.figure)

    return ax
