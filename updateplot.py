from pathlib import Path

from pipeline import update_dataset

if __name__ == '__main__':
    update_dataset(output_dir=Path('.'))
