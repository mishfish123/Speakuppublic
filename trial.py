import pandas
from openaustralia import OpenAustralia
import math

oa = OpenAustralia("AJT4oRBgm69pAze6h3GGVSMQ")
value = oa.get_representatives(int(3104))[0]['full_name'].split()
print(value)
df = pandas.read_csv('Rep.csv', engine='python')
result = df.loc[(df['Surname'] == value[-1]) & (df['First Name'] == value[0])]
if result.empty:
    result = df.loc[(df['Surname'] == value[-1]) & (df['Preferred Name'] == value[0])]
print(math.isnan(result['Email'].values[0]))
