'''
Backward-compatibility shim.

New code should import directly from `scraper` (for `load_mortagerate`) and
`plots` (for `plot_curve`). This module re-exports the old names so existing
imports keep working.
'''

from plots import plot_curve
from scraper import load_mortagerate

__all__ = ['load_mortagerate', 'plot_curve']
