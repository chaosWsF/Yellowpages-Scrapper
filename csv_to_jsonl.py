import pandas as pd
from yellowpages_scrapper import helper

keyword = 'Restaurants'
place = 'Edmonton AB'
fname = f'{helper(keyword)}_{helper(place)}_yellowpages_scraped_data'
df = pd.read_csv(f'{fname}.csv')
df.to_json(f'{fname}.jsonl', orient="records", lines=True)
