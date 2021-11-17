import pandas as pd
import numpy as np
import yfinance
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [12, 7]
plt.rc('font', size=14)

name = 'SPY'
ticker = yfinance.Ticker(name)
df = ticker.history(interval="1d",start="2019-1-15", end="2020-07-15")
df['Date'] = pd.to_datetime(df.index)
df['Date'] = df['Date'].apply(mpl_dates.date2num)
df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]



def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
  return support
def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
  return resistance

data = []
for i in range(2,df.shape[0]-2):
  if isSupport(df,i):
    data.append((df['Date'][i],df['Low'][i], 1))
  elif isResistance(df,i):
    data.append((df['Date'][i],df['High'][i], -1))



#print out levels and see lows and high and assign them a triangle


def plot_all():
  fig, ax = plt.subplots()
  candlestick_ohlc(ax,df.values,width=0.08, \
                   colorup='green', colordown='red', alpha=0.8)
  date_format = mpl_dates.DateFormatter('%d %b %Y')
  ax.xaxis.set_major_formatter(date_format)
  fig.autofmt_xdate()
  fig.tight_layout()
  for level in data:
    if level[2] == -1:
      plt.plot(level[0], level[1], marker='v', color='red')
    if level[2] == 1:
      plt.plot(level[0], level[1], marker='^', color='green')

  plt.show()


#plot_all()
total = 0
total1 = 0
count = 0
count1 = 0

# for stuff in data:
#   if stuff[2] == 1:
#     total -= stuff[1]
#     count += 1


#     while count1 > 0:
#       total1 -= stuff[1]
#       count1 -= 1
#     print("long: ", total, count)
#     print("cover: ", total1, count)


#   if stuff[2] == -1:
#     while count > 0:
#       total += stuff[1]
#       count -= 1


#     total1 += stuff[1]
#     count1 += 1
#     print("exit: ", total, count)
#     print("short: ", total1, count)

for stuff in data:
  if stuff[2] == 1:
    total -= stuff[1]
    count += 1


    while count1 > 0:
      total -= stuff[1]
      count1 -= 1

  if stuff[2] == -1:
    while count > 0:
      total += stuff[1]
      count -= 1


    total += stuff[1]
    count1 += 1
    

# for stuff in data:
#   if stuff[2] == 1:
#     while count1 > 0:
#       total -= stuff[1]
#       count1 -= 1
#     print("buy: ", total, count)
#   if stuff[2] == -1:
#     total += stuff[1]
#     count1 += 1
#     print("sell: ", total, count)




print(total)

plot_all()
