from datetime import timedelta

def date_fn(start, count, cal):
   alldates = []
   dates = []
   zerodates = [] #dates that are holidays and will be marked with 0 live hours
   for i in range(count):
      day = start+timedelta(days=i)
      day=day.date()
      year=day.year
      holidays = cal.holidays(year)
      holidates = [date for (date, _) in holidays]
      if day.isoweekday() < 6:
         if day not in holidates:
            dates.append(day)
         else:
            zerodates.append(day)
         alldates.append(day)
   return alldates, dates, zerodates