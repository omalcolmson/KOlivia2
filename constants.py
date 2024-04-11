'''
Script for holding storing global constants
'''
# ---- TIME DATA ----
amTimePhrases = [" am", " AM", " a.m.", " A.M.", " in the morning", ""]
pmTimePhrases = [" pm", " PM", " p.m.", " P.M.", " in the afternoon", " in the evening", " at night", ""]
oClock = [" o'clock", ""]

# ---- DATE DATA ----

months = {
    1: ["JANUARY", "JAN"],
    2: ["FEBRUARY", "FEB"],
    3: ["MARCH", "MAR"],
    4: ["APRIL", "APR"],
    5: ["MAY"],
    6: ["JUNE", "JUN"],
    7: ["JULY", "JUL"],
    8: ["AUGUST", "AUG"],
    9: ["SEPTEMBER", "SEPT", "SEP"],
    10: ["OCTOBER", "OCT"],
    11: ["NOVEMBER", "NOV"],
    12: ["DECEMBER", "DEC"],
} 

 #dict for storing the days of the week where monday starts at key value of 1 and sunday ends at key value of 7 and the values are a list of strings (in all caps) that represent the day of the week
daysOfTheWeek = {
    1: ["MONDAY", "MON"],
    2: ["TUESDAY", "TUE"],
    3: ["WEDNESDAY", "WED"],
    4: ["THURSDAY", "THU"],
    5: ["FRIDAY", "FRI"],
    6: ["SATURDAY", "SAT"],
    7: ["SUNDAY", "SUN"],
}

monthsofYear = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
monthsAbbrev = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

daysOfTheWeekAsStrs = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

timeOfDayPhrases = ["MORNING", "AFTERNOON", "EVENING", "NIGHT"] #only night uses "at" for the preposition

relativeToToday = ["TODAY", "THIS", "TOMORROW", "TONIGHT", "NEXT WEEK", "NEXT MONTH", "NEXT YEAR"]

have31Days = [
        "january",
        "march",
        "may",
        "july",
        "august",
        "october",
        "december",
        "01",
        "03",
        "05",
        "07",
        "08",
        "10",
        "12",
        "jan",
        "mar",
        "may",
        "jul",
        "aug",
        "oct",
        "dec",
    ]

have30Days = [
    "april",
    "june",
    "september",
    "november",
    "04",
    "06",
    "09",
    "11",
    "apr",
    "jun",
    "sept",
    "nov",
]
