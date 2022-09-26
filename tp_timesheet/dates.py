from datetime import timedelta

def date_fn(start, count):
   dates = []

   for i in range(count):
      day = start+timedelta(days=i)
      day=day.date()
      if day.isoweekday() < 6:

         dates.append(day)
   return dates