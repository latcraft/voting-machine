import re

from datetime import datetime
from itertools import groupby

def time(hour, minute):
  return datetime.today().replace(hour = hour, minute = minute, second = 0)

def in_voting_interval(vote_time, session_end_time):
  return (vote_time - session_end_time).total_seconds() < 15 * 60 and (session_end_time - vote_time).total_seconds() < 20 * 60

schedule = [
  { 'start': time(9, 0),   'end': time(10, 10) },
  { 'start': time(10, 30), 'end': time(11, 20) },
  { 'start': time(11, 40), 'end': time(12, 30) },
  { 'start': time(13, 40), 'end': time(14, 30) },
  { 'start': time(14, 50), 'end': time(15, 40) },
  { 'start': time(16, 0),  'end': time(16, 50) },
  { 'start': time(17, 10), 'end': time(18, 0) },
  { 'start': time(18, 20), 'end': time(19, 30) },
]

records = []

# Example: 2016-11-08 13:44:15 STATS: GREEN=4,YELLOW=5,RED=4
record_pattern = re.compile('^(?P<date_time>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+STATS:\s+GREEN=(?P<green>\d+),RED=(?P<red>\d+),YELLOW=(?P<yellow>\d+)$')

with open("/var/log/device.log", "r") as input:
  for line in input:
    for match in record_pattern.finditer(line):
      record = match.groupdict()
      record['date_time'] = datetime.strptime(record['date_time'], '%Y-%m-%d %H:%M:%S')
      if record['date_time'].date() == datetime.today().date():
        condition = lambda session: in_voting_interval(record['date_time'], session['end'])
        record['session'] = next(iter(filter(condition, schedule)), None)
        if record['session'] is not None:
          records.append(record)

print len(records)

for session, session_records in groupby(records, key = lambda record: record['session']['start']):
  for r in session_records:
    print str(int(r['green']))
  R = sum(int(r['red']) for r in session_records)
  Y = sum(int(r['yellow']) for r in session_records)
  G = sum(int(r['green']) for r in session_records)
  print str(G)
