import pandas as pd
import re

df = pd.read_csv("./data/reviews(DEPRECATED).csv", encoding="utf-8")
df['Review'] = df['Review'].apply(lambda x: re.sub("&#[0-9]{2,};","",str(x)))
df.to_csv("./data/reviews.csv",encoding="utf-8", index=False)
