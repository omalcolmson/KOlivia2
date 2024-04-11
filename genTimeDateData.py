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
                    while endMonthInt == startMonthInt and endDayInt <= startDayInt:
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    # if endMonthInt == 2 and startDayInt > 28:
                    #     endMonthInt += 1
                    #     endDayInt = 1 #move to next month
                    while endMonthInt == 2 and endDayInt > 28:
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
                    monthStr = random.choice(['0'+str(endMonthInt), str(endMonthInt)]) if endMonthInt < 10 else str(endMonthInt) #get str representation of monthInt and sometimes include leading 0
                    while endDayInt > 30 and var.monthsAbbrev[endMonthInt-1].lower() not in var.have31Days: #if the month doesn't have 31 days
                        endMonthInt = random.choice(range(1, 13))
                        endDayInt = random.choice(range(1, 32))
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
    Generates list of time period phrases with specified start and end times in the following formats:
    - HH:MM - HH:MM
    - from HH:MM to HH:MM
    - from HH:MM until HH:MM
    - HH:MM to HH:MM
    - at HH:MM - HH:MM
    - at HH:MM to HH:MM
    - at HH:MM until HH:MM

    I don't think time periods need to be exhaustive, but they should be able to capture the general format of time periods. 

    This function ONLY handles times expressed using digits, as the process of handling times expressed through words (not digits) was requiring too much time and effort at the moment. Plan on returning to this later. 

    This function also only creates time periods in increments of 1 hour to simplify the process of generating the training data.

    '''
 
    exactTimePeriods = []
    startTimes = []
    endTimes = []
    for minute in range(0, 60):
        for hour in range(1, 13): #morning times
            #get str representation of hour and randomly choose to include leading 0 if hour and minute < 10
            hourStr = random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            amTimePhrase = random.choice(var.amTimePhrases[:3]+[" o'clock", ""])
            minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
            timeAsWords = f"{n2w(hourStr)}{' ' + minutesAsWords if minute != 0 else ''}"
            if amTimePhrase == " in the morning":
                timeStr = f"{hourStr}:{minuteStr}{var.oClock[0] if minute == 0 else ''}{amTimePhrase}" # "at HH:MM o'clock in the morning" or "for HH:MM o'clock in the morning"
                timeStr2 = f"{timeAsWords}{var.oClock[0] if minute == 0 else ''}{amTimePhrase}" # e.g., "at two thirty am"
            else:
                timeStr = f"{hourStr}:{minuteStr}{amTimePhrase}"  # "at HH:MM am" or "for HH:MM am" or "HH:MM am"
                timeStr2 = f"{timeAsWords}{amTimePhrase}" # e.g., "at two thirty am"
            startTimes.append((timeStr, AM_START_LABEL))
            startTimes.append((timeStr2, AM_START_LABEL))

            hour = hour + 1 if hour < 12 else 1 #increment hour by 1
            hourStr = random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)
            amTimePhrase = random.choice(var.amTimePhrases)
            minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
            timeAsWords = f"{n2w(hourStr)}{' ' + minutesAsWords if minute != 0 else ''}"
            if amTimePhrase == " in the morning":
                timeStr = f"{hourStr}:{minuteStr}{var.oClock[0] if minute == 0 else ''}{amTimePhrase if hour <= 11 else random.choice(var.pmTimePhrases)}" # "at HH:MM o'clock in the morning" or "for HH:MM o'clock in the morning"
                timeStr2 = f"{timeAsWords}{var.oClock[0] if minute == 0 else ''}{amTimePhrase if hour<= 11 else random.choice(var.pmTimePhrases)}" # e.g., "at two thirty am"
            else:
                timeStr = f"{hourStr}:{minuteStr}{amTimePhrase if hour <= 11 else random.choice(var.pmTimePhrases)}"  # "at HH:MM am" or "for HH:MM am" or "HH:MM am"
                timeStr2 = f"{timeAsWords}{amTimePhrase if hour <= 11 else random.choice(var.pmTimePhrases)}" # e.g., "at two thirty am"
            endTimes.append((timeStr, AM_END_LABEL if hour <= 11 else PM_END_LABEL))
            endTimes.append((timeStr2, AM_END_LABEL if hour <= 11 else PM_END_LABEL))
        
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
            startTimes.append((timeStr, PM_START_LABEL))
            startTimes.append((timeStr2, PM_START_LABEL))

            hour = hour + 1 if hour < 12 else 1
            hourStr = random.choice(["0" + str(hour), str(hour)]) if hour < 10 else str(hour)
            pmTimePhrase = selectPMPhrase(hour)
            minutesAsWords = n2w(minute) if minute > 9 and minute != 0 else 'o ' + n2w(minute)
            timeAsWords = f"{n2w(hourStr)}{' ' + minutesAsWords if minute != 0 else ''}"
            if pmTimePhrase == " at night":
                timeStr = f"{hourStr}:{minuteStr}{var.oClock[0] if minute == 0 else ''}{pmTimePhrase if hour <= 11 else random.choice(var.amTimePhrases)}" #can include o'clock
                timeStr2 = f"{timeAsWords}{var.oClock[0] if minute == 0 else ''}{pmTimePhrase if hour <= 11 else random.choice(var.amTimePhrases)}" # e.g., "at two thirty at night" 
            else:
                timeStr = f"{hourStr}:{minuteStr}{pmTimePhrase if hour <= 11 else random.choice(var.amTimePhrases)}"
                timeStr2 = f"{timeAsWords}{pmTimePhrase if hour <= 11 else random.choice(var.amTimePhrases)}" # e.g., "at two thirty pm"
            endTimes.append((timeStr, PM_END_LABEL if hour <= 11 else AM_END_LABEL))
            endTimes.append((timeStr2, PM_END_LABEL if hour <= 11 else AM_END_LABEL))

        for hour in range(0, 24): #for 24 hour time
            # TODO: fix end times for 24 hour time
            hourStr = ""
            if hour == 0:
                hourStr = "00"
            else:
                hourStr = "0" + str(hour) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            timeStr = f"{hourStr}:{minuteStr}"
            startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            timeStr = f"{hourStr}:{minuteStr} hours"
            startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            
            if hour == 0:
                hourPhrase = random.choice(["zero zero", "zero hundred", "twenty-four hundred"])
            else:
                hourPhrase = n2w(hour) + " hundred"
            if minute > 0 and minute < 10:
                timeStr = f"{hourPhrase} zero {n2w(minute)}"
                startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            elif minute >= 10:
                timeStr = f"{hourPhrase} {n2w(minute)}" #e.g., "twenty hundred thirty"
                startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
                timeStr = f"{hourPhrase} {n2w(minute//10)} {n2w(minute%10)}" #e.g., "twenty hundred three zero"
                startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
            elif minute == 0:
                timeStr = f"{hourPhrase} hours"
                startTimes.append((timeStr, MILITARY_TIME_START_LABEL))
        
        for hour in range(23, -1, -1): 
            hourStr = ""
            if hour == 0:
                hourStr = "00"
            else:
                hourStr = "0" + str(hour) if hour < 10 else str(hour)
            minuteStr = "0" + str(minute) if minute < 10 else str(minute)
            timeStr = f"{hourStr}:{minuteStr}"
            endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
            timeStr = f"{hourStr}:{minuteStr} hours"
            endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
            
            if hour == 0:
                hourPhrase = random.choice(["zero zero", "zero hundred", "twenty-four hundred"])
            else:
                hourPhrase = n2w(hour) + " hundred"
            if minute > 0 and minute < 10:
                timeStr = f"{hourPhrase} zero {n2w(minute)}"
                endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
            elif minute >= 10:
                timeStr = f"{hourPhrase} {n2w(minute)}" #e.g., "twenty hundred thirty"
                endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
                timeStr = f"{hourPhrase} {n2w(minute//10)} {n2w(minute%10)}" #e.g., "twenty hundred three zero"
                endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
            elif minute == 0:
                timeStr = f"{hourPhrase} hours"
                endTimes.append((timeStr, MILITARY_TIME_END_LABEL))
    
    for idx in range(0, len(startTimes)):
        exactTimePeriods.append((startTimes[idx], endTimes[idx]))

    return exactTimePeriods
