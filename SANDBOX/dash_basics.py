from pybaseball import statcast
data = statcast(start_dt='2017-06-15', end_dt='2017-06-28')
data.head(20)