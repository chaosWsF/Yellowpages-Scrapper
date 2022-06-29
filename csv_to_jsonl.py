import pandas as pd

keyword = 'Restaurants'
place = 'Edmonton AB'
fname = f'{keyword}_{place}_yellowpages_scraped_data'
df = pd.read_csv(f'{fname}.csv')
df.to_json(f'{fname}.jsonl', orient="records", lines=True)
