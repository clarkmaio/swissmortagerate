

from datetime import datetime
from swiss_mortage_rate import SwissMortageRate
from data_loader import URL
import yaml

if __name__ == '__main__':


    smr = SwissMortageRate()
    smr.plot(save_path='./swiss_mortage_rate.png')
    smr.data.to_parquet(path='./swiss_mortage_rate.parquet')

    

    metadata = {
        'rundate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': URL,
    }
    with open('./metadata.yml', 'w') as f:
        yaml.dump(metadata, f)