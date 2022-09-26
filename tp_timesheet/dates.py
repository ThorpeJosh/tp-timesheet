from datetime import date, timedelta
# from tp_timesheet import DATE

def date_fn(start, count):
   # if count:
   #    delta = count
   # else:
   #    delta= 1
   dates = []

   for i in range(count):
      day = start+timedelta(days=i)
      day=day.date()
      if day.isoweekday() < 6:

         dates.append(day)
   return dates