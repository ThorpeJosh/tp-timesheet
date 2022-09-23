from datetime import date, timedelta
# from tp_timesheet import DATE

def date_fn(start, count):
   # if start:
   start_date = start
   # else:  
   #    start_date= date(2022, 5, 15)
   if count:
      delta = count
   else:
      delta= 1
   dates = []

   for i in range(delta):
      day = start_date+timedelta(days=i)
      day_string= day.strftime("%d/%m/%Y")
      day=day.date()
      if day.isoweekday() < 6:

         dates.append(day)
   print(dates)

# start_date = date(2022, 9, 23)
# date_fn(start_date, 4)