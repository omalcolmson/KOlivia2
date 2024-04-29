import random
import string
import json
import spacy
import pandas as pd
import constants as var
from datetime import date, datetime
from spacy.tokens import DocBin
from num2words import num2words as n2w #might need to run pip install num2words in terminal to run
from word2number import w2n #might need to run pip install words2num in terminal to run

# ---------- GLOBAL VARIABLES/CONSTANTS ----------------
CURRENT_YEAR = date.today().year
AM_START_LABEL = "AM_TIME_START"
AM_END_LABEL = "AM_TIME_END"
PM_START_LABEL = "PM_TIME_START"
PM_END_LABEL = "PM_TIME_END"
MILITARY_TIME_START_LABEL = "MILITARY_TIME_START"
MILITARY_TIME_END_LABEL = "MILITARY_TIME_END"

DATE_START_LABEL = "DATE_START"
DATE_END_LABEL = "DATE_END"

# ---------- HELPER FUNCTIONS ----------------

def writeTextToFile( fileName: str, textList: list) -> None:
    '''
    Writes the given text to the given file name
    '''
    with open(fileName, "w") as f:
        for text in textList:
            # f.write(text[0] + "\n") #just writes the string to the file
            f.write(str(text) + "\n")

def dayIntsToStr(dayInt: int) -> str:
    '''
    For handling converting the day as an integer to a string with the appropriate suffixes of "st", "nd", "rd", or "th"
    '''
    if dayInt > 3 and dayInt < 21:
            dayStr = str(dayInt) + "th"
    else:
        remainder = dayInt % 10
        if remainder == 1:
            dayStr = str(dayInt) + "st"
        elif remainder == 2:
            dayStr = str(dayInt) + "nd"
        elif remainder == 3:
            dayStr = str(dayInt) + "rd"
        else:
            dayStr = str(dayInt) + "th"

    return dayStr

def selectPMPhrase(hour: int) -> str:
    '''
    Randomly selects a time phrase for the PM time period based on the hour

    pmTimePhrases = [" pm", " PM", " p.m.", " P.M.", " in the afternoon", " in the evening", " at night", ""]

    '''
    pm = [" pm", " PM", " p.m.", " P.M.", ""]
    if hour < 6: #12-6 -> afternoon
        return random.choice(pm+[" in the afternoon"])
    elif hour >= 6 and hour < 9: #6-9 -> evening
        return random.choice(pm+[" in the evening"])
    elif hour >= 9 and hour < 12:
        return random.choice(pm+[" at night"])
    

# ---------- GENERATING TRAINING DATA FUNCTIONS ----------------

# ---------- DATE GENERATION FUNCTIONS ----------------

def handleDateStrVars(dateStr: str) -> str:
    '''
    Handles all format variations of lowercase, uppercase, and capitalization for date strings
    '''
    dateStr = random.choice([dateStr, dateStr.lower(), dateStr.lower().capitalize()])
    if len(dateStr) == 3:
        dateStr = random.choice([dateStr, dateStr + '.', dateStr + ','])
    return dateStr

def addDOTW(startOEnd: int) -> list:
    '''
    Adds days of the week to the exactDatesData.csv file 

    Dates formatted this way will have to be implied relative to the current day
    '''
    label = DATE_START_LABEL if startOEnd == 0 else DATE_END_LABEL
    dotw = []
    for k,v in var.daysOfTheWeek.items():
        for day in v: #iterates through each str format of the dotw 
            dotw.append((day, label)) #all capps
            dotw.append((day.lower(), label)) #all lower
            dotw.append((day.lower().capitalize(), label)) #capitalized

    return dotw
def genExactDates() -> list:
    '''
    Generates a list of exact dates in the following formats:

    - MM/DD/YYYY
    - MM/DD (current year implied)
    - YYYY/MM/DD
    - Month, DayInt, Year
    - Month, DayInt (current year implied)
    - DOTW, Month, DayInt, Year (e.g., Monday, January 1st, 2020)
    - DOTW, Month, DayInt (current year implied)
    - DOTW, MM/DD/YYYY
    - DOTW, MM/DD (current year implied)
    - DOTW, YYYY/MM/DD

   Dates are returned as a list in the form of a tuple:
   (DateStr, LABEL)

    '''
    exactDates = []
    for monthInt in range(1, 13):
        for dayInt in range(1, 32):
            for yearInt in range(CURRENT_YEAR, CURRENT_YEAR+3): #TODO: consider another method to optimize runtime
                # DATES WITH INTS
                # randomly choose month form as 01 or 1 as long as monthInt < 10
                if monthInt == 2 and dayInt > 28:
                    continue #skip this iteration for now
                monthStr = random.choice(['0'+str(monthInt), str(monthInt)]) if monthInt < 10 else str(monthInt) #get str representation of monthInt and sometimes include leading 0
                if dayInt > 30 and var.monthsAbbrev[monthInt-1].lower() not in var.have31Days: #if the month doesn't have 31 days
                    continue #skip this iteration and continue to next month
                #anything past this should be a month in have31Days
                #get str representation of day and randomly choose to include leading 0 if dayInt < 10
                dayStr = random.choice(['0' + str(dayInt), str(dayInt)]) if dayInt < 10 else str(dayInt)
                yearStr = str(yearInt)

                # MM/DD/YYYY, MM/DD, AND YYYY/MM/DD FORMS
                
                dateStr1 = f"{monthStr}/{dayStr}/{yearStr}" # "on MM/DD/YYYY", "for MM/DD/YYYY", or "MM/DD/YYYY"
                dateStr2 = f"{monthStr}/{dayStr}" # "on MM/DD", "for MM/DD", or "MM/DD"
                dateStr3 = f"{yearStr}/{monthStr}/{dayStr}"
                exactDates.append((dateStr1, DATE_START_LABEL))
                exactDates.append((dateStr2, DATE_START_LABEL))
                exactDates.append((dateStr3, DATE_START_LABEL))

                # Month, DayInt, Year and Month, DayInt forms
                monthStr = random.choice(var.months.get(monthInt)) #get month str randomly as either full or abbreviated
                monthStr = handleDateStrVars(monthStr) #handles all format variations of lowecase, uppercase, and capitalization 
                dayStr = dayIntsToStr(dayInt)
            
                dateStr4 = f"{monthStr} {dayStr}, {yearStr}" # Month, DayInt, Year form
                dateStr5 = f"{monthStr} {dayStr}" # Month, DayInt form
                exactDates.append((dateStr4, DATE_START_LABEL))
                exactDates.append((dateStr5, DATE_START_LABEL))
                
                # forms that include DOTW
                theDate = date(yearInt, monthInt, dayInt) #create date object for accurate DOTW calculation
                dotwAsStr = random.choice(var.daysOfTheWeek[theDate.isoweekday()]) #get the weekday as an int and use it as an index 
                dotwAsStr = handleDateStrVars(dotwAsStr)
                dateStr6 = f"{dotwAsStr} {monthStr} {dayStr}, {yearStr}" # "on DOTW, Month DayInt, Year" or "for DOTW, Month DayInt, Year" or "DOTW, Month DayInt, Year"
                monthStr = '0' + str(monthInt) if monthInt < 10 else str(monthInt)
                dayStr = '0' + str(dayInt) if dayInt < 10 else str(dayInt)
                dateStr7 = f"{dotwAsStr} {monthStr}/{dayStr}/{yearInt}" # "on DOTW, MM/DD/YYYY" or "for DOTW, MM/DD/YYYY" or "DOTW, MM/DD/YYYY" 
                dateStr8 = f"{dotwAsStr} {yearInt}/{monthStr}/{dayStr}" # "on DOTW, YYYY/MM/DD" or "for DOTW, YYYY/MM/DD" or "DOTW, YYYY/MM/DD"
                exactDates.append((dateStr6, DATE_START_LABEL))
                exactDates.append((dateStr7, DATE_START_LABEL))
                exactDates.append((dateStr8, DATE_START_LABEL))

                if yearInt == CURRENT_YEAR: #if the year is the current year, want to account for dateStrs that imply current year
                    #need to reassign
                    monthStr = random.choice(var.months.get(monthInt)) #full month name or abbreviated
                    monthStr = handleDateStrVars(monthStr) #handles all format variations of lowercase, uppercase, capitalized, and abbrev w or w/o period
                    dayStr = dayIntsToStr(dayInt)
                    
                    dateStr9 = f"{dotwAsStr} {monthStr} {dayStr}" # "on DOTW, Month DayInt" or "for DOTW, Month DayInt" or "DOTW, Month DayInt" all for the current year
                    dateStr10 = f"{dotwAsStr} {monthStr}/{dayStr}" # "on DOTW, MM/DD" or "for DOTW, MM/DD" or "DOTW, MM/DD" all for the current year
                    exactDates.append((dateStr9,  DATE_START_LABEL))
                    exactDates.append((dateStr10, DATE_START_LABEL))
    
    return exactDates

def genDatePeriods() -> list: 
    '''
    Generates start and end dates for date periods. The dates will be generated in the same format as the exact dates function. 

    - (M1/D1 - M2/D2/YYYY) where current year is implied and M1, M2, D1, and D2 can be completely different values
    - (M1/D1 - M2/D2) where current year is implied and M1, M2, D1, and D2 can be completely different values
    - YYYY/MM/DD
    - Month1, DayInt1, to Month2, DayInt2, Year
    - Month1, DayInt1 to Month2, DayInt2 (current year implied)

    - DOTW, Month, DayInt, Year (e.g., Monday, January 1st, 2020)
    - DOTW, Month, DayInt (current year implied)
    - DOTW, MM/DD/YYYY
    - DOTW, MM/DD (current year implied)
    - DOTW, YYYY/MM/DD
    
    '''
    #TODO: there are some errors in the date generation where the start month is later than the end month or the start day is later than the end day, but this could be validated later as we only need the model to identify in he context of a sentence, what is being specified as a start date and what is being specified as an end date
    datePeriods = []
    for yearInt in range(CURRENT_YEAR, CURRENT_YEAR+3): 
        for startMonthInt in range(1, 13):
            for startDayInt in range(1, 32):   
                if startMonthInt == 2 and startDayInt > 28:
                    continue #skip this iteration for now
                monthStr = random.choice(['0'+str(startMonthInt), str(startMonthInt)]) if startMonthInt < 10 else str(startMonthInt) #get str representation of monthInt and sometimes include leading 0
                if startDayInt > 30 and var.monthsAbbrev[startMonthInt-1].lower() not in var.have31Days: #if the month doesn't have 31 days
                    continue #skip this iteration and continue to next month
                endYear = random.choice([True, False]) #randomly choose whether to have an end year or not
                if endYear: #IF WE MAKE THE YEAR DIFFERENT
                    endYearStr = str(yearInt + 1)
                    startYrStr = str(yearInt)
                    # rules can change about the values of D1 and D2 because of the month
                    endMonthInt = random.choice(range(1, 13))
                    endDayInt = random.choice(range(1, 32))
                    # if the months are the same, the end day must be greater than the start day
                    while endMonthInt == 2 and endDayInt > 28:
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    monthStr = random.choice(['0'+str(endMonthInt), str(endMonthInt)]) if endMonthInt < 10 else str(endMonthInt) #get str representation of monthInt and sometimes include leading 0
                    while endDayInt > 30 and var.monthsAbbrev[endMonthInt-1].lower() not in var.have31Days: #if the month doesn't have 31 days
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    endMonthStr = random.choice(['0'+str(endMonthInt), str(endMonthInt)]) if endMonthInt < 10 else str(endMonthInt)
                    endDayStr = random.choice(['0'+str(endDayInt), str(endDayInt)]) if endDayInt < 10 else str(endDayInt)
                    # M1/D1 - M2/D2/YYYY
                    dateStartStr = f"{monthStr}/{startDayInt}/{startYrStr}"
                    dateEndStr = f"{endMonthStr}/{endDayStr}/{endYearStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                    # YYYY/MM/DD - YYYY/MM/DD
                    dateStartStr = f"{startYrStr}/{monthStr}/{startDayInt}"
                    dateEndStr = f"{endYearStr}/{endMonthStr}/{endDayStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                    # Month1, DayInt1, to Month2, DayInt2, Year
                    startMonthStr = random.choice(var.months.get(startMonthInt))
                    startMonthStr = handleDateStrVars(startMonthStr)
                    endMonthStr = random.choice(var.months.get(endMonthInt))
                    endMonthStr = handleDateStrVars(endMonthStr)
                    startDayStr = dayIntsToStr(startDayInt)
                    endDayStr = dayIntsToStr(endDayInt)
                    dateStartStr = f"{startMonthStr} {startDayStr}, {startYrStr}"
                    dateEndStr = f"{endMonthStr} {endDayStr}, {endYearStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                    # DOTW, Month, DayInt, Year
                    theDate = date(yearInt, startMonthInt, startDayInt)
                    dotwAsStr = random.choice(var.daysOfTheWeek[theDate.isoweekday()])
                    dotwAsStr = handleDateStrVars(dotwAsStr)
                    startMonthStr = random.choice(var.months.get(startMonthInt))
                    startMonthStr = handleDateStrVars(startMonthStr)
                    startDayStr = dayIntsToStr(startDayInt)
                    dateStartStr = f"{dotwAsStr} {startMonthStr} {startDayStr}, {startYrStr}"
                    theDate = date(yearInt, endMonthInt, endDayInt)
                    dotwAsStr = random.choice(var.daysOfTheWeek[theDate.isoweekday()])
                    dotwAsStr = handleDateStrVars(dotwAsStr)
                    endMonthStr = random.choice(var.months.get(endMonthInt))
                    endMonthStr = handleDateStrVars(endMonthStr)
                    endDayStr = dayIntsToStr(endDayInt)
                    dateEndStr = f"{dotwAsStr} {endMonthStr} {endDayStr}, {endYearStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                else: #IF WE MAKE THE YEAR THE SAME
                    # if months are the same, the end day must be greater than the start day
                    # else the end month must be greater than the start month and the days can be anything
                    endMonthInt = random.choice(range(1, 13))
                    endDayInt = random.choice(range(1, 32))
                    # if the months are the same and the days are the same or the end day happens before the start day, randomly select dates again
                    while endMonthInt == startMonthInt and endDayInt <= startDayInt:
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    while endMonthInt == 2 and endDayInt > 28: #exclude leap years 
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    while endDayInt > 30 and var.monthsAbbrev[endMonthInt-1].lower() not in var.have31Days: #if the month doesn't have 31 days
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    # if endMonthInt == 2 and startDayInt > 28:
                    #     endMonthInt += 1
                    #     endDayInt = 1 #move to next month
                    monthStr = random.choice(['0'+str(startMonthInt), str(startMonthInt)]) if startMonthInt < 10 else str(startMonthInt) #get str representation of monthInt and sometimes include leading 0
                    endMonthStr = random.choice(['0'+str(endMonthInt), str(endMonthInt)]) if endMonthInt < 10 else str(endMonthInt)
                    endDayStr = random.choice(['0'+str(endDayInt), str(endDayInt)]) if endDayInt < 10 else str(endDayInt)
                    startYrStr = str(yearInt)
                    # M1/D1 - M2/D2 where current year is implied
                    dateStartStr = f"{monthStr}/{startDayInt}"
                    dateEndStr = f"{endMonthStr}/{endDayStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                    # Month1, DayInt1 to Month2, DayInt2 where current year is implied
                    startMonthStr = random.choice(var.months.get(startMonthInt))
                    startMonthStr = handleDateStrVars(startMonthStr)
                    endMonthStr = random.choice(var.months.get(endMonthInt))
                    endMonthStr = handleDateStrVars(endMonthStr)
                    startDayStr = dayIntsToStr(startDayInt)
                    endDayStr = dayIntsToStr(endDayInt)
                    dateStartStr = f"{startMonthStr} {startDayStr}"
                    dateEndStr = f"{endMonthStr} {endDayStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))
                    # DOTW1, Month1, DayInt1, to DOTW2, Month2, DayInt2 where current year is implied
                    theDate = date(yearInt, startMonthInt, startDayInt)
                    dotwAsStr = random.choice(var.daysOfTheWeek[theDate.isoweekday()])
                    dotwAsStr = handleDateStrVars(dotwAsStr)
                    startMonthStr = random.choice(var.months.get(startMonthInt))
                    startMonthStr = handleDateStrVars(startMonthStr)
                    startDayStr = dayIntsToStr(startDayInt)
                    dateStartStr = f"{dotwAsStr} {startMonthStr} {startDayStr}"
                    theDate = date(yearInt, endMonthInt, endDayInt)
                    dotwAsStr = random.choice(var.daysOfTheWeek[theDate.isoweekday()])
                    dotwAsStr = handleDateStrVars(dotwAsStr)
                    endMonthStr = random.choice(var.months.get(endMonthInt))
                    endMonthStr = handleDateStrVars(endMonthStr)
                    endDayStr = dayIntsToStr(endDayInt)
                    dateEndStr = f"{dotwAsStr} {endMonthStr} {endDayStr}"
                    datePeriods.append(((dateStartStr, DATE_START_LABEL), (dateEndStr, DATE_END_LABEL)))

    return datePeriods


# ---------- TIME GENERATION FUNCTIONS ----------------

def selectPMPhrase(hour: int) -> str:
    '''
    Randomly selects a time phrase for the PM time period based on the hour

    pmTimePhrases = [" pm", " PM", " p.m.", " P.M.", " in the afternoon", " in the evening", " at night", ""]

    '''
    pm = [" pm", " PM", " p.m.", " P.M.", ""]
    choice = ''
    if hour < 6: #12-6 -> afternoon
        choice = random.choice(pm+[" in the afternoon"])
    elif hour >= 6 and hour < 9: #6-9 -> evening
        choice = random.choice(pm+[" in the evening"])
    elif hour >= 9 and hour < 12:
        choice = random.choice(pm+[" at night"])
    return choice

def randomTimePhrase(am_pm: int, hour: int) -> str:
    '''
    Args:
    - am_pm: 0 for am, 1 for pm

    Rule for selecting time phrases 
    [ NUMBER TIME ] + ([ optional = 'o'clock'] + [optional = 'in the morning', 'in the afternoon', 'in the evening', 'at night'] ) || [optional = 'am', 'pm']

    '''
    #TODO: these are repeated variables I made locally when testing in a separate file
    amTimePhrases = ["in the morning", ""]
    pmTimePhrases = ["in the afternoon", "in the evening", "at night", ""]
    oClock = ["o'clock", ""]  
    amFormats = ["am", "AM", "a.m.", "A.M."]
    pmFormats = ["pm", "PM", "p.m.", "P.M."]
    if am_pm == 0: # AM times
        phrase1 = " ".join([random.choice(oClock), random.choice(amTimePhrases)])
        phrase2 = random.choice(amFormats)
    else: # PM times
        phrase1 = selectPMPhrase(hour)
        phrase2 = selectPMPhrase(hour)
    return random.choice([phrase1, phrase2]).strip() #randomly adds space since we still want to identify it as a time phrase

def formatHour(hour: int, milTime: bool) -> str:
    '''
    Returns a string of the hour in a random format of string digits
    Works for both regular and military time

    Args:
    - hour: int

    Formats:
    - "HH"
    - "0H"
    - "H"

    '''
    if milTime:
        return "0" + str(hour) if hour < 10 else str(hour)
    else:
        return random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)

def formatMinute(minute: int) -> str:
    '''
    Returns a string of the minute in a random format of string digits
    Works for both regular and military time

    Args:
    - minute: int

    Formats:
    - "MM"

    '''
    return "0" + str(minute) if minute < 10 else str(minute)

def format24HrHR(hour: int) -> str:
    '''
    Returns the 24-hour format of the hour in the time pronunciation

    Args:
    - hour: int

    '''
    
    if hour < 10:
        return n2w(0) + " " + n2w(hour) # e.g., zero two (hundred hours)
    else:
        return n2w(hour)

def format24HrMIN(minute: int) -> str:
    '''
    Returns the 24-hour format of the minute in the time pronunciation

    Args:
    - minute: int

    '''
    strOptions = []
    if minute == 0:
        return '' #just return empty string if minutes are zero
    elif minute in range(1, 10):
        strOptions.append(n2w(0) + " " + n2w(minute)) # e.g., zero five
        strOptions.append("oh " + n2w(minute)) # e.g., oh five
        strOptions.append("o " + n2w(minute)) # e.g., five
    else:
        strOptions.append(n2w(minute)) # e.g., twenty
        strOptions.append(n2w(minute//10) + " " + n2w(minute%10)) # e.g., two zero
        strOptions.append(n2w(minute//10) + "-" + n2w(minute%10)) # e.g., two-zero
    
    return random.choice(strOptions)

def format24HrTime(time: tuple, hourStr: str, minuteStr: str) -> str:
    '''
    Returns the 24-hour format of the time

    Args:
    - time: tuple with (hourInt, minuteInt)
    - hourStr: str of the hour reflecting 24-hour time pronunciation 
    - minuteStr: str of the minute(s) formatted in 24-hour time pronunciation
    '''
    militaryTime = ''
    minute = time[1]
    if minute == 0:
        militaryTime = hourStr + " hundred"
        militaryTime += random.choice([" hours", ""]) #randomly adds hours at the end if the minute is zero (e.g., zero one hundred vs zero one hundred hours)
    else:
        militaryTime = hourStr + " " + minuteStr
    return militaryTime

def timeAsWords(hour: int, minute: int, type: int) -> str:
    '''
    Returns the time as words (e.g., two thirty, fourteen hundred hours)

    Args:
    - hour: int
    - minute: int
    - type: 0 for regular time, 1 for military time

    '''

    if type == 0 : #regular time
        if minute in range (1, 10):
            timeStr = n2w(hour) + " oh " + n2w(minute)
        elif minute == 0:
            timeStr = n2w(hour) + " o'clock"
        else:
            timeStr = n2w(hour) + " " + n2w(minute) # e.g., two thirty
    else: #military time
        timeStr = format24HrHR(hour) + " " + format24HrMIN(minute)
            
    return timeStr


def genExactTimes() -> list:
    '''
    Exact Time Formats: 
    
    - HH:MM (24hr)
    - HH:MM (12hr)


    Possible time of day phrases that may follow exact times:
    - in the morning
    - in the afternoon
    - in the evening
    - at night
    - am, AM, a.m., A.M.
    - pm, PM, p.m., P.M.
    - o'clock
    - hours (for 24 hour time)

    These phrases will be considered part of the labeled entity for the time

    (TimeStr, LABEL)

    '''
    exactTimes = []

    for minute in range(0, 60):
        for hour in range(1, 13): #morning times
            #get str representation of hour and randomly choose to include leading 0 if hour and minute < 10
            hourStr = random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            amTimePhrase = random.choice(var.amTimePhrases)
            minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
            timeAsWords = f"{n2w(hourStr)}{' ' + minutesAsWords if minute != 0 else ''}"
            if amTimePhrase == " in the morning":
                timeStr = f"{hourStr}:{minuteStr}{var.oClock[0] if minute == 0 else ''}{amTimePhrase}" # "at HH:MM o'clock in the morning" or "for HH:MM o'clock in the morning"
                timeStr2 = f"{timeAsWords}{var.oClock[0] if minute == 0 else ''}{amTimePhrase}" # e.g., "at two thirty am"
            else:
                timeStr = f"{hourStr}:{minuteStr}{amTimePhrase}"  # "at HH:MM am" or "for HH:MM am" or "HH:MM am"
                timeStr2 = f"{timeAsWords}{amTimePhrase}" # e.g., "at two thirty am"
            exactTimes.append((timeStr, AM_START_LABEL))
            exactTimes.append((timeStr2, AM_START_LABEL))
                
        for hour in range(12, 0, -1): #afternoon times, going backwards 
            hourStr = random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            pmTimePhrase = selectPMPhrase(hour)
            minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
            timeAsWords = f"{n2w(hourStr)}{' ' + minutesAsWords if minute != 0 else ''}"
            if pmTimePhrase == " at night":
                timeStr = f"{hourStr}:{minuteStr}{var.oClock[0] if minute == 0 else ''}{pmTimePhrase}" #can include o'clock
                timeStr2 = f"{timeAsWords}{var.oClock[0] if minute == 0 else ''}{pmTimePhrase}" # e.g., "at two thirty at night" 
            else:
                timeStr = f"{hourStr}:{minuteStr}{pmTimePhrase}"
                timeStr2 = f"{timeAsWords}{pmTimePhrase}" # e.g., "at two thirty pm"
            exactTimes.append((timeStr,PM_START_LABEL))
            exactTimes.append((timeStr2, PM_START_LABEL))
        
        for hour in range(0, 24): #for 24 hour time
            hourStr = ""
            if hour == 0:
                hourStr = "00"
            else:
                hourStr = "0" + str(hour) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            timeStr = f"{hourStr}:{minuteStr}"
            exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            timeStr = f"{hourStr}:{minuteStr} hours"
            exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            
            if hour == 0:
                hourPhrase = random.choice(["zero zero", "zero hundred", "twenty-four hundred"])
            else:
                hourPhrase = n2w(hour) + " hundred"
            if minute > 0 and minute < 10:
                timeStr = f"{hourPhrase} zero {n2w(minute)}"
                exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            elif minute >= 10:
                timeStr = f"{hourPhrase} {n2w(minute)}" #e.g., "twenty hundred thirty"
                exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
                timeStr = f"{hourPhrase} {n2w(minute//10)} {n2w(minute%10)}" #e.g., "twenty hundred three zero"
                exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            elif minute == 0:
                timeStr = f"{hourPhrase} hours"
                exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))

            # if hourStr == '00':
            #     timeAsWords = n2w(hourStr) + " hundred" + (" "+n2w(minuteStr) if minute != 0 else '')
            # elif hour != 0 and hour < 10:
            #     timeAsWords = 'zero ' + n2w(hourStr[1]) + " hundred" 
            #     if minute != 0:
            #         timeAsWords += " "+(n2w(minuteStr) if minute >= 10 else 'zero ' + n2w(minuteStr[-1]))
            # else: #hours >= 10 
            #     timeAsWords = n2w(hourStr) + " hundred " + n2w(minuteStr) #year provides the correct format for 24 hour time
            # timeStr = f"{timeAsWords.strip()} hours"
            # exactTimes.append((timeStr, MILITARY_TIME_START_LABEL))
    
    return exactTimes

def genExactTimePeriods() -> list:
    '''
    time formats:
    - 12:00 am
    - 12 am
    - 2:00 pm
    - 02:00 pm
    - 14:00 pm
    - 14:00
    - fourteen hundred hours
    - 2:00 in the morning

    Minutes stay the same for simplicity of generating training data.
   
    Returns a list of timeframes which are nested tupe pairs : 
    [
        (
            (startTime, label), (endTime, label)
        )
    ]
    '''
    timeframes = []
    
    for hour in range(0, 24):
        for minute in range(0, 60):
            if hour == 0: #ONLY MILITARY TIMES
                # 24 HOUR TIME IN WORD FORMATS
                startHr = format24HrHR(hour)
                endHr = format24HrHR(hour+1)
                startMin = format24HrMIN(minute)
                endMin = format24HrMIN(minute)
                start24time = format24HrTime((hour, minute), startHr, startMin)
                end24time = format24HrTime((hour+1, minute), endHr, endMin)
                timeframes.append(((start24time, MILITARY_TIME_START_LABEL), (end24time, MILITARY_TIME_END_LABEL)))

                # 24 HOUR TIME IN DIGIT FORMAT
                startHr = formatHour(hour, True)
                endHr = formatHour(hour+1, True)
                startMin = formatMinute(minute)
                endMin = formatMinute(minute)
                start24time = startHr + ":" + startMin
                end24time = endHr + ":" + endMin
                timeframes.append(((start24time, MILITARY_TIME_START_LABEL), (end24time, MILITARY_TIME_END_LABEL)))
            
            elif hour < 11: #AM AND PM TIMES -> will run from 1 am to 11 am
                pass
                # 12 HOUR AM TIME IN DIGIT FORMATS
                startHr = formatHour(hour, False)
                endHr = formatHour(hour+1, False)
                startMin = formatMinute(minute)
                endMin = formatMinute(minute)
                start12Time = startHr + ":" + startMin + randomTimePhrase(0, hour)
                end12Time = endHr + ":" + endMin + randomTimePhrase(1, hour)
                timeframes.append(((start12Time, AM_START_LABEL), (end12Time, AM_END_LABEL)))

                # 12 HOUR AM TIME IN WORD FORMATS
                minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
                timeAsWords1 = f"{n2w(hour)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeAsWords2 = f"{n2w(hour+1)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeStr1 = f"{timeAsWords1}{randomTimePhrase(0, hour)}" # e.g., "at two thirty am"
                timeStr2 = f"{timeAsWords2}{randomTimePhrase(0, hour+1)}" # e.g., "at two thirty am"
                timeframes.append(((timeStr1, AM_START_LABEL), (timeStr2, AM_END_LABEL)))

            elif hour == 11: #AM AND PM TIMES -> will run from 11 am to 12 pm
                startHr = formatHour(hour, False)
                endHr = formatHour(hour+1, False)
                startMin = formatMinute(minute)
                endMin = formatMinute(minute)
                start12Time = startHr + ":" + startMin + randomTimePhrase(0, hour) #11 -> am
                end12Time = endHr + ":" + endMin + randomTimePhrase(1, hour) #12 -> pm
                timeframes.append(((start12Time, AM_START_LABEL), (end12Time, PM_END_LABEL)))

            # 11 AM to 1 PM in WORD FORMAT
                minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
                timeAsWords1 = f"{n2w(hour)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeAsWords2 = f"{n2w(hour+1)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeStr1 = f"{timeAsWords1}{randomTimePhrase(0, hour)}" # e.g., "at two thirty am"
                timeStr2 = f"{timeAsWords2}{randomTimePhrase(1, hour+1)}" # e.g., "at two thirty am"
                timeframes.append(((timeStr1, AM_START_LABEL), (timeStr2, PM_END_LABEL)))
            else: 
                # 12 HOUR PM TIME IN DIGIT FORMATS, 12 pm to 1 am
                startHr = ''
                endHr = ''
                if hour == 12:
                    startHr = formatHour(hour, False)
                    endHr = formatHour(1, False)
                elif hour >= 12: 
                    startHr = formatHour(hour-12, False)
                    endHr = formatHour(hour-11, False)
                startMin = formatMinute(minute)
                endMin = formatMinute(minute)
                start12Time = startHr + ":" + startMin + randomTimePhrase(1, int(startHr))
                end12Time = endHr + ":" + endMin + (randomTimePhrase(1, int(endHr)) if int(startHr) != 11 else randomTimePhrase(0, int(startHr)))
                timeframes.append(((start12Time, PM_START_LABEL), (end12Time, PM_END_LABEL if int(startHr) != 11 else AM_END_LABEL)))

                # 12 HOUR PM TIME IN WORD FORMATS (12 pm to 1 am)
                
                minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
                timeAsWords1 = f"{n2w(hour-12)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeAsWords2 = f"{n2w(hour-11)}{' ' + minutesAsWords if minute != 0 else ''}"
                timeStr1 = f"{timeAsWords1}{randomTimePhrase(1, int(hour-12))}" # e.g., "at two thirty am"
                timeStr2 = f"{timeAsWords2}{randomTimePhrase(0, int(hour-11))}" # e.g., "at two thirty am"
                timeframes.append(((timeStr1, PM_START_LABEL), (timeStr2, PM_END_LABEL if int(hour-12) != 11 else AM_END_LABEL)))

                # ONLY MILITARY TIMES
                # 24 HOUR TIME IN WORD FORMATS
                startHr = format24HrHR(hour)
                if hour == 23:
                    endHr = format24HrHR(0)
                else:
                    endHr = format24HrHR(hour+1)
                startMin = format24HrMIN(minute)
                endMin = format24HrMIN(minute)
                start24time = format24HrTime((hour, minute), startHr, startMin)
                end24time = format24HrTime((hour+1, minute), endHr, endMin)
                timeframes.append(((start24time, MILITARY_TIME_START_LABEL), (end24time, MILITARY_TIME_END_LABEL)))

                # 24 HOUR TIME IN DIGIT FORMAT
                startHr = formatHour(hour, True)
                if hour == 23:
                    endHr = formatHour(0, True)
                else:
                    endHr = formatHour(hour+1, True)
                startMin = formatMinute(minute)
                endMin = formatMinute(minute)
                start24time = startHr + ":" + startMin
                end24time = endHr + ":" + endMin
                timeframes.append(((start24time, MILITARY_TIME_START_LABEL), (end24time, MILITARY_TIME_END_LABEL)))
                                  
    return timeframes

def genRelativeDates() -> list:
    '''
    Relative date phrases:
    Phrases that only specify a date relative to the current date
    - tomorrow
    - today 
    - x days from now
    - next week
    - in (an, int) week(s) (from now)
    - next month
    - in (an, int) month(s) (from now)
    - next year
    - in (an, int) year(s) (from now)
    - this week
    - this month
    '''
    RELATIVE_DATE_LABEL = "RELATIVE_DATE"
    relativeDates = []
    dateFrameWords = ["day", "week", "month", "year"]
    conjunctions = ["from now", "from today", ""]

    for word in dateFrameWords: 
        for i in range(1, 9): #will aribitrarily choose 1-8 for the number of days, weeks, months, years will be more limited
            if i == 1: #singular, 1 week, 1 month, 1 year
                prefixes = ["in", "in a", ""]
                for prefix in prefixes:
                    for conjunction in conjunctions:
                        if prefix == "" and conjunction == "":
                            pass #skip this iteration if they are both nothing
                        else:
                            if "a" not in prefix: #conjunctions that use 'in'
                                phrase = prefix + " " + str(i) + " " + word + " " + conjunction
                                phrase = phrase.strip()
                                relativeDates.append((phrase, RELATIVE_DATE_LABEL))
                                phrase = prefix + " " + n2w(i) + " " + word + " " + conjunction
                                phrase = phrase.strip()
                                relativeDates.append((phrase, RELATIVE_DATE_LABEL))
                            else: #conjunctions that use 'in a'
                                phrase = prefix + " " + word + " " + conjunction
                                phrase = phrase.strip()
                                relativeDates.append((phrase, RELATIVE_DATE_LABEL))
            else: #plural
                prefixes = ["in", ""]
                for prefix in prefixes:
                    for conjunction in conjunctions:
                        if prefix == conjunction:
                            pass
                        else:
                            phrase = prefix + " " + str(i) + " " + word + "s " + conjunction
                            relativeDates.append((phrase.strip(), RELATIVE_DATE_LABEL))
                            phrase = prefix + " " + n2w(i) + " " + word + "s " + conjunction
                            relativeDates.append((phrase.strip(), RELATIVE_DATE_LABEL))

        dateFrames = ["beginning of", "end of", "start of", "end of", "middle of"]
        prefixes = ["at the", "for the", "around the"]
        connectors = ["this", "the", "next"]
        if word == "day":
            pass
        else:
            for prefix in prefixes:
                for connector in connectors:
                    for dateFrame in dateFrames:
                        phrase = f"{prefix} {dateFrame} {connector} {word}"#e.g., "at the beginning of the week"
                        relativeDates.append((phrase, RELATIVE_DATE_LABEL))

    return relativeDates

def genRelativeTimes() -> list:
    '''
    Relative time phrases:
    Phrases that only specify a time relative to the current time
    - in (an, int) hour(s)
    - in (an, int) minute(s)
    '''
    RELATIVE_TIME_LABEL = "RELATIVE_TIME"
    relativeTimes = []
    timeFrameWords = ["morning", "afternoon", "evening", "night"]
    relativeDateFrames = ["this", "for the", "for this", "in the", "around the", "later in the", "later this", "later today"]

    for word in relativeDateFrames:
        for time in timeFrameWords:
            phrase = word + " " + time
            relativeTimes.append((phrase, RELATIVE_TIME_LABEL))

    for hour in range(1, 24): #upper limit is 24 because 24 hours later is the next day
        if hour == 1:
            pass
            conjunctions = {"in", "about", "for", "around"}
            for conjunction in conjunctions:
                if conjunction == "in":
                    phrase = f"{conjunction} {hour} hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} about {hour} hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} an hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} a hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} {hour} hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} {n2w(hour)} hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} an hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} a hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
        else: 
            conjunctions = {"in", "about", "around", "starting in", "beginning in"}
            for conjunction in conjunctions:
                if "in" in conjunction:
                    phrase = f"{conjunction} {hour} hours"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} about {hour} hours"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} an hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                    phrase = f"{conjunction} a hour"
                    relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} {hour} hours from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} {n2w(hour)} hours from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} an hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))
                phrase = f"{conjunction} a hour from now"
                relativeTimes.append((phrase.strip(), RELATIVE_TIME_LABEL))

    return relativeTimes


def genRelativeDateTimes() -> list:
    '''
    Relative time and date phrases:
    Phrases that specify a relative time and date
    - tomorrow morning, tomorrow afternoon, tomorrow evening, night
    '''
    relativeDateTimes = []
    label = "RELATIVE_DATE_TIME"
    timeFrameWords = ["morning", "afternoon", "evening", "night"]
    conjunctions = ["in the", "around the", "later in the", "during the"]
    dateTimeFrames = ["tomorrow"]
    for dateTime in dateTimeFrames:
        for time in timeFrameWords:
            for conjunction in conjunctions:
                phrase = dateTime + " " + time
                relativeDateTimes.append((phrase, label))
                phrase = dateTime + " " + conjunction + " " + time
                relativeDateTimes.append((phrase, label))


    return relativeDateTimes