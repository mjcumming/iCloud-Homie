
import pytz 
import datetime 
local_tz = pytz.timezone('US/Eastern') 
timeStamp = 1574622729211
date = datetime.datetime.fromtimestamp(timeStamp / 1000, local_tz) 
print(date)
print(date.strftime("%Y%m%d %I:%M:%S %p") )
