from datetime import timedelta

def date_fn(start, count, cal):
   dates = []
   for i in range(count):
      day = start+timedelta(days=i)
      day=day.date()
      year=day.year
      holidays = cal.holidays(year)
      holidates = [date for (date, _) in holidays]
      if day.isoweekday() < 6:
         if day not in holidates:
            dates.append(day)
   return dates