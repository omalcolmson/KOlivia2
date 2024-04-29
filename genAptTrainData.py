import random
import string
import json
import spacy
from spacy.tokens import DocBin
import pandas as pd
import constants as var
import promptConstants as pc
import genTimeDateData as gtt
from datetime import date, datetime
from spacy.tokens import DocBin
from num2words import num2words as n2w #might need to run pip install num2words in terminal to run
from word2number import w2n #might need to run pip install words2num in terminal to run


# ---------- HELPER FUNCTIONS ----------------

def locSubstr(text: str, substr: str) -> tuple:
    '''
    Locates a given substring in a text and returns the start and end indices of the substring in the text
    '''
    start = text.find(substr)
    end = start + len(substr)
    return (start, end)

def selectRandomDF(df: pd.DataFrame) -> list:
    '''
    Selects a random row from a given DataFrame
    '''
    # row = random.choice(df.index) #selects a random row in the dataframe
    # return df.iloc[row]
    retList = []
    num_rows = df.shape[0]
    num_cols = df.shape[1]
    idx = random.randint(0, num_rows-1) #selects a random row in the dataframe
    pair = []

    for i in range(num_cols): #iterates through the columns
        if i == 1 or i == 3: #
            pair.append(df.iat[idx, i])
            retList.append(tuple(pair))
            pair = []
        else:
            pair.append(df.iat[idx, i])
    
    return retList

def listToListDicts(lst: list) -> list:
    '''
    Converts a list of tuples to a list of dictionaries
    '''
    retList = []
    for tup in lst:
        retList.append({'text': tup[0], 'entities': tup[1]})
    return retList

# ---------- GENERATING THE ACTUAL TRAINING DATA ----------------
'''
Functions to run to generate the training data for the model.

These functions will insert the dates and times into texts and then write the texts to a file, so they can be loaded into a spacy model. 

For each prompt type, the function will:
    1. read the relevant CSV file into a pandas DF
    2. iterate through each row in the DF to extract the text and its corresponding label(s)
    3. insert the date or time into the text
    4. pass that text in locSubstr function to get the start and end indices for each inserted date or time
    5. create a tuple with the text and a nested tuple inside of a list containing the start index, end index, and label for that particular entity
    6. append that tuple to the data list
    7. write the data list to a file so that the data can be reviewed before passing into the model or used at a later time.
    8. return the data list to be passed into the spacy model

Problem is, there can be many 'types' of prompts that we want to generate. 
Absolute:
    - exact single date (e.g, "Mark my calendar for 12/25/2025")
    - exact single time where current date is implied (e.g., "Schedule a meeting with John for 3:00 PM")
    - start time and start date specified (e.g., "I will have a meeting with John on 5/25 at 3:00 PM")
    - start date and start and end time specified (e.g., "Meet with Alex on 4/13 from 2:00 to 4:00 PM")
    - start and end date with no times specified (e.g., "Mark my calendar as out of office starting on 5/25 to 5/30")
    - start and end date with start and end times specified (e.g., "I will be out of office from 5/25 at 3:00 PM to 5/30 at 5:00 PM")

Relative:
    - appointment with a relative date and exact time ("Mark my calendar for a dentist appointment in 3 days at 2:00 PM")
    - appointment with a relative date period ("Schedule a follow up meeting with John in 2 weeks ")
    - appointment with a relative end time ("Schedule my lunch break for an hour from now.")
    - appointment with a relative time period ("Remind me to turn in my project in 2 hours")

'''
# ---------- PROPAGATING PROMPTS WITH EXTRACTED DATA ----------------

#TODO: consider the syntax of some of the prompts and the phrases being inserted into them -- some sound awkard


def genAptTypeG(relativeDateTime, reason):
    '''
    Returns a random prompt for an appointment that includes:
    - a relative date
    - a relative time
    - a reason for the appointment
    '''

    typeG = [
        f"Remind me to {reason} {relativeDateTime}.",
        f"Remind me {relativeDateTime} to {reason}.",
        f"Add an event to my calendar for time to {reason} {relativeDateTime}.",
        f"Add an event to my calendar to {reason} {relativeDateTime}.",
        f"Block off time for {reason} {relativeDateTime}.",
        f"Block off time to {reason} {relativeDateTime}.",
        f"Block off {relativeDateTime} to {reason}.",
        f"Create a calendar event to {reason} {relativeDateTime}.",
        f"Create an event to {reason} {relativeDateTime}.",
        f"Create a calendar event {relativeDateTime} to {reason}.",
        f"Mark my calendar to {reason} {relativeDateTime}.",
        f"Mark my calendar {relativeDateTime} to {reason}.",
        f"Schedule a meeting to {reason} {relativeDateTime}.",
        f"Schedule a meeting {relativeDateTime} to {reason}.",
        f"Schedule a meeting to {reason} {relativeDateTime}.",
        f"Set up a meeting to {reason} {relativeDateTime}.",
        f"Set up a meeting {relativeDateTime} to {reason}.",
    ]

    return random.choice(typeG)

def genAptTypeF(relativeTime, reason):
    '''
    Returns a random prompt for an appointment that includes:
    - a relative time
    - a reason for the appointment
    '''
    typeF = [ 
        f"Remind me to {reason} in {relativeTime}.",
        f"Mark my calendar to {reason} in {relativeTime}.",
        f"Mark my calendar {relativeTime} to {reason}.",
        f"Schedule a meeting to {reason} in {relativeTime}.",
        f"Schedule a meeting {relativeTime} to {reason}.", 
        f"Schedule an appointment to {reason} {relativeTime}.",
        f"Add an event to my calendar to {reason} in {relativeTime}.",
        f"Add an event to my calendar {relativeTime} to {reason}.",
        f"Block off time to {reason} {relativeTime}.",
        f"Block off {relativeTime} to {reason}.",
        f"Block off {relativeTime} in my calendar.",
        f"Set up a time to {reason} {relativeTime}.",
        f"Put an event to {reason} {relativeTime} on my calendar.",
        f"Create an event to {reason} {relativeTime}.",
        f"Create an event {relativeTime} to {reason}.",
        f"{relativeTime.capitalize()}, create an event to {reason}.",
        f"{relativeTime.capitalize()}, mark my calendar to {reason}.",
        f"{relativeTime.capitalize()}, schedule a meeting to {reason}.",
        f"{relativeTime.capitalize()}, block off time to {reason}.",
    ]

    return random.choice(typeF)

def genAptTypeE(relativeDate, reason):
    '''
    Returns a random prompt for an appointment that includes:
    - a relative date
    - a reason for the appointment
    '''
    typeE = [
        f"Mark my calendar {relativeDate} to {reason}.",
        f"Mark my calendar to {reason} {relativeDate}.",
        f"Mark my calendar to {reason} in {relativeDate}.",
        f"Schedule an appointment to {reason} {relativeDate}.",
        f"Schedule a meeting to {reason} {relativeDate}.",
        f"Schedule a meeting {relativeDate} to {reason}.", #order
        f"Add an event to my calendar to {reason} {relativeDate}.",
        f"Block off time for {reason} in {relativeDate}.",
        f"Block off {relativeDate} to {reason}.", #order
        f"Set up a time to {reason} {relativeDate}.",
        f"Put {reason} on my calendar for {relativeDate}.",
        f"Remind me on {relativeDate} to {reason}.",
        f"Pencil in {reason} in {relativeDate}.",
        f"Arrange a meeting to {reason} {relativeDate}.",
        f"Book a time to {reason} {relativeDate}.",
        f"Create an event to {reason} {relativeDate}.",
        f"Block off my calendar to {reason} in {relativeDate}.",
        f"On {relativeDate}, schedule a meeting to {reason}.",
    ]
    return random.choice(typeE)

def genAptTypeD(reason, startDateStr, endDateStr):
    ''' 
    Returns a random prompt for an appointment that includes:
    - a start date
    - an end date
    - (sometimes) a reason for the appointment
    '''
    typeD = [
        f"Mark my calendar as out of office starting on {startDateStr} to {endDateStr}.",
        f"Schedule my vacation from {startDateStr} to {endDateStr}.",
        f"Schedule my vacation from {startDateStr} - {endDateStr}.", #hypenated date
        f"From {startDateStr} to {endDateStr}, block off time in my calendar for {reason}.",
        f"Add an event to my calendar from {startDateStr} until {endDateStr}.",
        f"Add an event to my calendar from {startDateStr} - {endDateStr}.", #hyphenated date
        f"Block off time from {startDateStr} to {endDateStr} to {reason}.",
        f"Block off time on my caendar for {reason} starting from {startDateStr} to {endDateStr}.", #order
        f"Block off my calendar from {startDateStr} to {endDateStr}.",
        f"Put an event on my calendar from {startDateStr} to {endDateStr}.",
        f"Create an event from {startDateStr} to {endDateStr} to {reason}.",
        f"Create an event to {reason} from {startDateStr} to {endDateStr}.",
        f"Starting on {startDateStr} to {endDateStr}, put an event on my calendar for {reason}.",
        f"I will be out of office from {startDateStr} until {endDateStr}.",
        f"Block off time in my calendar from {startDateStr} to {endDateStr} for {reason}.",
        f"Put my trip from {startDateStr} to {endDateStr} on my calendar.",
        f"I will be out of office for {reason} from {startDateStr} to {endDateStr}.",
        f"I will be out of office from {startDateStr} to {endDateStr} for {reason}.",
        f"I will be out of office from {startDateStr} to {endDateStr}.",
        f"I will be out of office from {startDateStr} until {endDateStr}.",
        f"I will be out of office from {startDateStr} to {endDateStr} inclusive.",
        f"I will be out of office starting on {startDateStr} to {endDateStr}.",
        f"I will be out of office starting from {startDateStr} until {endDateStr}.",
        f"Mark my calendar as out of office starting from {startDateStr} to {endDateStr}.",
        f"Mark my calendar as out of office from {startDateStr} to {endDateStr}.",
        f"Schedule my vacation for {reason} from {startDateStr} to {endDateStr}.",
        f"Schedule my vacation from {startDateStr} to {endDateStr} for {reason}.",
        f"From {startDateStr} to {endDateStr}, block off time for {reason} in my calendar.",
        f"From {startDateStr} to {endDateStr}, block off time in my calendar for {reason}.",
        f"From {startDateStr} to {endDateStr}, block off time for {reason} on my calendar.",
        f"From {startDateStr} to {endDateStr}, block off time on my calendar for {reason}.",
        f"Add an event to my calendar for {reason} from {startDateStr} to {endDateStr}.",
        f"Add an event to my calendar from {startDateStr} to {endDateStr} for {reason}.",
        f"Block off time for {reason} from {startDateStr} to {endDateStr}.",
        f"Block off time in my calendar for {reason} from {startDateStr} to {endDateStr}.",
        f"Block off time on my calendar from {startDateStr} to {endDateStr} for {reason}.",
        f"Put {reason} from {startDateStr} to {endDateStr} on my calendar.",
        f"Put an event from {startDateStr} to {endDateStr} on my calendar for {reason}.",
        f"Create an event for {reason} from {startDateStr} to {endDateStr}.",
        f"Create an event from {startDateStr} to {endDateStr} for {reason}.",
        f"Starting from {startDateStr}, put an event for {reason} on my calendar until {endDateStr}.",
        f"I will be out of office for {reason} starting from {startDateStr} to {endDateStr}.",
        f"I will be out of office from {startDateStr} to {endDateStr} for {reason}.",
        f"Block off time in my calendar for {reason} starting from {startDateStr} to {endDateStr}.",
        f"Put my trip on my calendar from {startDateStr} to {endDateStr}.",
        f"Put my trip from {startDateStr} to {endDateStr} on my calendar.",

    ]
    return random.choice(typeD)

def genAptTypeC(singleDate, reason, timeStart, timeEnd):
    '''
    Returns a random prompt for an appointment that includes:
    - a single date
    - a start time
    - an end time
    - a reason for the appointment
    '''
    typeC = [
        f"Mark my calendar for the {singleDate} from {timeStart} to {timeEnd} for {reason}.",
        f"Mark my calendar from {timeStart} - {timeEnd} for {reason} for the {singleDate}.", #hypenated time
        f"Mark my calendar from {timeStart} to {timeEnd} for {reason} on the {singleDate}.",
        f"Schedule a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"Schedule a meeting from {timeStart} to {timeEnd} for {reason} on {singleDate}.", # order
        f"Schedule a meeting for {reason} from {timeStart} to {timeEnd} on {singleDate}.", # order
        f"Add an event to my calendar for {reason} on {singleDate} starting at {timeStart} and ending at {timeEnd}.",
        f"Block off time for {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"Block off {singleDate} from {timeStart} to {timeEnd} to {reason}.", #order
        f"Set up a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd},",
        f"Put {reason} on my calendar for {singleDate} from {timeStart} to {timeEnd},",
        f"Remind me on {singleDate} from {timeStart} to {timeEnd} to {reason}.",
        f"Pencil in {reason} on {singleDate} from {timeStart} to {timeEnd},",
        f"Arrange a meeting to {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"Book a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"Create an event for {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"Create an event on {singleDate} from {timeStart} to {timeEnd} for {reason}.", #order
        f"Create an event for {reason} on {singleDate} from {timeStart} to {timeEnd}.", #order
        f"Block off my calendar for {reason} on {singleDate} from {timeStart} to {timeEnd}.",
        f"On {singleDate} from {timeStart} to {timeEnd}, schedule a meeting for {reason}.",
        f"Starting from {timeStart} to {timeEnd} on {singleDate}, block out time to {reason}.", #order
        f"On {singleDate}, from {timeStart} to {timeEnd}, schedule a meeting for {reason}.",
        f"Starting from {singleDate}, from {timeStart} to {timeEnd}, block out time to {reason}.",
        f"Block out time to {reason} from {timeStart} to {timeEnd} on {singleDate}.",
        f"Block out time on {singleDate} from {timeStart} to {timeEnd} for {reason}.",
        f"Block out time on {singleDate} to {reason} from {timeStart} to {timeEnd}.",
        f"{singleDate}, from {timeStart} to {timeEnd}, reserve time for {reason}.",
        f"Reserve time for {reason} on {singleDate}, from {timeStart} to {timeEnd}.",
        f"Reserve time on {singleDate}, from {timeStart} to {timeEnd}, for {reason}.",
        f"Reserve time on {singleDate} for {reason} from {timeStart} to {timeEnd}.",
        f"From {singleDate}, block off time from {timeStart} to {timeEnd} for {reason}.",
        f"From {singleDate}, schedule a meeting from {timeStart} to {timeEnd} for {reason}.",
        f"From {singleDate} to {reason}, schedule a meeting from {timeStart} to {timeEnd}.",
        f"{singleDate} is booked from {timeStart} to {timeEnd} for {reason}.",
        f"{singleDate}, {reason}, from {timeStart} to {timeEnd}, mark my calendar.",
        f"{singleDate}, {reason}, mark my calendar from {timeStart} to {timeEnd}.",
        f"Schedule a meeting from {singleDate} to {reason} on {timeStart} to {timeEnd}.",
        f"Set up a meeting for {reason} from {singleDate} to {timeStart} to {timeEnd}.",
        f"Create an event for {reason} from {singleDate} to {timeStart} on {timeEnd}.",
        f"Arrange a meeting for {reason} from {singleDate} to {timeStart} on {timeEnd}.",
        f"Put {reason} on my calendar from {singleDate} to {timeStart} for {timeEnd}.",
        f"Remind me from {singleDate} to {timeStart} to {reason} on {timeEnd}.",
        f"Pencil in from {singleDate} to {timeStart} to {reason} on {timeEnd}.",
        f"Block off from {singleDate} to {timeStart} for {timeEnd} to {reason}.",
        f"Add an event for {reason} on {singleDate} starting from {timeStart} until {timeEnd}.",
        f"Create an event on {singleDate} from {timeStart} to {timeEnd} for {reason}.",

    ]
    return random.choice(typeC)

def genAptTypeB(singleDate, reason, singleTime):
    '''
    Returns a random prompt for an appointment that includes:
    - a single date
    - a single time
    - a reason for the appointment
    '''
    typeB = [
        f"Mark my calendar for {singleDate} at {singleTime} for {reason}.",
        f"Mark my calendar for {reason} at {singleTime} on {singleDate}.", #order
        f"Mark my calendar for {singleTime} to {singleDate} at {singleTime}.", #order
        f"Schedule a meeting for {reason} on {singleDate} at {singleTime}.",
        f"Schedule a meeting {singleDate} at {singleTime} for {reason}.",
        f"Schedule a meeting at {singleTime} on {singleDate} for {reason}.",
        f"Schedule a meeting at {singleTime} to {reason} on {singleDate}.",
        f"Add an event to my calendar for {reason} on {singleDate} starting at {singleTime}.",
        f"Add an event on my calendar for {singleDate} starting at {singleTime} for {reason}.", #order
        f"Add an event on my calendar starting at {singleTime} on for {singleDate} for {reason}.", #order
        f"Block off time to {reason} on {singleDate} at {singleTime}.",
        f"Block off time on {singleDate} at {singleTime} to {reason}.",
        f"Block off time at {singleTime} on {singleDate} to {reason}.",
        f"Block off my calendar for {reason} on {singleDate} at {singleTime}.",
        f"Block off my calendar on {singleDate} at {singleTime} for {reason}.",
        f"Block off my calendar at {singleTime} on {singleDate} for {reason}.",
        f"Set up a meeting for {reason} on {singleDate} at {singleTime}.",
        f"Set up a meeting on {singleDate} at {singleTime} to {reason}.",
        f"Set up a meeting at {singleTime} on {singleDate} to {reason}.",
        f"Put {reason} on my calendar for {singleDate} at {singleTime}.",
        f"Put {reason} on my calendar at {singleTime} on {singleDate}.",
        f"Remind me on {singleDate} at {singleTime} to {reason}.",
        f"Remind me at {singleTime} on {singleDate} to {reason}.",
        f"Pencil in {reason} on {singleDate} at {singleTime}.",
        f"Arrange a meeting to {reason} on {singleDate} at {singleTime}.",
        f"Arrange a meeting on {singleDate} at {singleTime} to {reason}.",
        f"Arrange a meeting at {singleTime} on {singleDate} to {reason}.",
        f"Book a meeting for {reason} on {singleDate} at {singleTime}.",
        f"Book a meeting on {singleDate} at {singleTime} to {reason}.",
        f"Book a meeting at {singleTime} to {reason} on {singleDate}.",
        f"Create an event for {reason} on {singleDate} at {singleTime}.",
        f"Create an event on {singleDate} at {singleTime} to {reason}.",
        f"On {singleDate} at {singleTime}, schedule a meeting to {reason}.",
        f"At {singleTime} on {singleDate}, block out time to {reason}.", #order
    ]
    return random.choice(typeB)

def genAptTypeA(singleDate, reason):
    '''
    Returns a random prompt for an appointment that includes:
    - a single date
    - a reason for the appointment
    '''
    typeA = [
        f"Mark my calendar for {singleDate} for {reason}.",
        f"Mark my calendar for {reason} on {singleDate}.",
        f"Mark my calendar to {reason} on {singleDate}.",
        f"Schedule an appointment for {reason} on {singleDate}.",
        f"Schedule a meeting for {reason} on {singleDate}.",
        f"Schedule a meeting on {singleDate} for {reason}.", #order
        f"Add an event to my calendar for {reason} on {singleDate}.",
        f"Block off time for {reason} on {singleDate}.",
        f"Block off {singleDate} to {reason}.", #order
        f"Set up a time to {reason} on {singleDate}.",
        f"Put {reason} on my calendar for {singleDate}.",
        f"Remind me on {singleDate} to {reason}.",
        f"Pencil in {reason} on {singleDate}.",
        f"Arrange a meeting to {reason} on {singleDate}.",
        f"Book a meeting with {reason} on {singleDate}.",
        f"Create an event for {reason} on {singleDate}.",
        f"Block off my calendar for {reason} on {singleDate}.",
        f"On {singleDate}, schedule a meeting to {reason}.",
    ]
    return random.choice(typeA)

def createAnnotation(prompt: str, entityList: list) -> tuple:
    '''
    Creates the annotation tuple for a single prompt given a list of entities and their respective labels 

    Args:
    - prompt: the text used for training
    - entityList: a list of tuples containing the substrings that will be passed into locSubstr to get the start and end indices and their respective labels
    - labels: a list of labels for the entities

    Returns:
    - a tuple containing the prompt and a list of tuples containing the start and end indices and labels for the entities
        Format: 
        ("Tokyo Tower is 333m tall.", [(0, 11, "BUILDING")]),
    
    '''

    sample = []
    for pair in entityList: #iterate through list of entities by tuple
        text = pair[0]
        label = pair[1]
        start, end = locSubstr(prompt, text)
        sample.append((start, end, label))

    return tuple([prompt, sample])



def genPrompts() -> list:
    '''
    Generates the prompts for the model to train on

    training_data = [
    ("Tokyo Tower is 333m tall.", [(0, 11, "BUILDING")]),
    ]
    '''
    #TODO: need to generate prompts with relative dates and time data

    reasonLabel = "REASON"
    data = []
    # read in the csv file
    relativeDatesDF = pd.read_csv("RawTrainData/relativeDatePeriodsData.csv", index_col=0)
    relativeTimesDF = pd.read_csv("RawTrainData/relativeTimePeriodsData.csv", index_col=0)
    relativeDateTimesDF = pd.read_csv("RawTrainData/relativeDateTimePeriodsData.csv", index_col=0)

    # # COLS: Text, Label
    # singleDatesDF = pd.read_csv("RawTrainData/exactDatesData.csv", index_col=0)
    # # COLS: Start_Date, Start_Label, End_Date, End_Label
    # datePeriodsDF = pd.read_csv("RawTrainData/datePeriodsData.csv", index_col=0)
    # # COLS: Text, Label
    # singleTimesDF = pd.read_csv("RawTrainData/exactTimesData.csv", index_col=0)
    # # COLS: Start_Time, Start_Label, End_Time, End_Label
    # timePeriodsDF = pd.read_csv("RawTrainData/timePeriodsData.csv", index_col=0)

    for i in range(1000): #changed to 500 just to test the generation of prompts with relative dates and times
        relativeDateTuple = selectRandomDF(relativeDatesDF)
        relativeTimeTuple = selectRandomDF(relativeTimesDF)
        relativeDateTimeTuple = selectRandomDF(relativeDateTimesDF)
    #     singleDateTuple = selectRandomDF(singleDatesDF)
    #     datePeriodTuple = selectRandomDF(datePeriodsDF)
    #     singleTimeTuple = selectRandomDF(singleTimesDF)
    #     timePeriodTuple = selectRandomDF(timePeriodsDF)
    
    # events/appts with relative dates
        relativeDate = relativeDateTuple[0][0]
        relativeDateLabel = relativeDateTuple[0][1]
        reason = random.choice(pc.actions)
        aptE = genAptTypeE(relativeDate, reason)
        sample = createAnnotation(aptE, [(relativeDate, relativeDateLabel), (reason, reasonLabel)])
        data.append(sample)

    # events/appts with relative times
        relativeTime = relativeTimeTuple[0][0]
        relativeTimeLabel = relativeTimeTuple[0][1]
        reason = random.choice(pc.actions)
        aptF = genAptTypeF(relativeTime, reason)
        sample = createAnnotation(aptF, [(relativeTime, relativeTimeLabel), (reason, reasonLabel)])
        data.append(sample)

    # events/appts with relative dates and times
        relativeDateTime = relativeDateTimeTuple[0][0]
        relativeDateTimeLabel = relativeDateTimeTuple[0][1]
        reason = random.choice(pc.actions)
        aptG = genAptTypeG(relativeDateTime, reason)
        sample = createAnnotation(aptG, [(relativeDateTime, relativeDateTimeLabel), (reason, reasonLabel)])
        data.append(sample)
        

    # # events/appts with 1 date no times
    #     singleDate = singleDateTuple[0][0]
    #     singleDateLabel = singleDateTuple[0][1]
    #     reason = random.choice(pc.actions) #randomly select a reason for the event from actions list
    #     aptA = genAptTypeA(singleDate, reason)
    #     if reason in aptA:
    #         sample = createAnnotation(aptA, [(singleDate, singleDateLabel), (reason, reasonLabel)])
    #     else:
    #         sample = createAnnotation(aptA, [(singleDate, singleDateLabel)])
    #     # print(sample)
    #     data.append(sample)

    #     # events/appts with 1 date and 1 time
    #     singleTime = singleTimeTuple[0][0]
    #     singleTimeLabel = singleTimeTuple[0][1]
    #     aptB = genAptTypeB(singleDate, reason, singleTime)
    #     if reason in aptB:
    #         sample = createAnnotation(aptB, [(singleDate, singleDateLabel), (singleTime, singleTimeLabel), (reason, reasonLabel)])
    #     else:
    #         sample = createAnnotation(aptB, [(singleDate, singleDateLabel), (singleTime, singleTimeLabel)])
    #     # print(sample)
    #     data.append(sample)

    #     # # events/appts with 1 date and a start and end time
    #     # print(timePeriodTuple)
    #     timeStartTuple = timePeriodTuple[0]
    #     timeEndTuple = timePeriodTuple[1]
    #     timeStart = timeStartTuple[0]
    #     timeStartLabel = timeStartTuple[1]
    #     timeEnd = timeEndTuple[0]
    #     timeEndLabel = timeEndTuple[1]
    #     aptC = genAptTypeC(singleDate, reason, timeStart, timeEnd)
    #     if reason in aptC:
    #         sample = createAnnotation(aptC, [(singleDate, singleDateLabel), (timeStart, timeStartLabel), (timeEnd, timeEndLabel), (reason, reasonLabel)])
    #     else:
    #         sample = createAnnotation(aptC, [(singleDate, singleDateLabel), (timeStart, timeStartLabel), (timeEnd, timeEndLabel)])
    #     # print(sample)
    #     data.append(sample)

    #     # events/appts with 2 dates and no times
    #     startDate = datePeriodTuple[0]
    #     endDate = datePeriodTuple[1]
    #     startDateStr = startDate[0]
    #     startDateLabel = startDate[1]
    #     endDateStr = endDate[0]
    #     endDateLabel = endDate[1]
    #     aptD = genAptTypeD(reason, startDateStr, endDateStr)
    #     if reason in aptD:
    #         sample = createAnnotation(aptD, [(startDateStr, startDateLabel), (endDateStr, endDateLabel), (reason, reasonLabel)])
    #     else:
    #         sample = createAnnotation(aptD, [(startDateStr, startDateLabel), (endDateStr, endDateLabel)])
    #     data.append(sample)

    return data


def main():

    # testing with a small batch
    small_batch = genPrompts() #small list of prompts
    listofDicts = listToListDicts(small_batch)

    with open("PreparedTrainData/relative_prompts_sample.json", "w") as f:
        json.dump(listofDicts, f, indent=2)

    # saving it with spacy docbin
    nlp = spacy.blank("en") # is this supposed to be en_core_web_sm?
    # nlp = spacy.load("en_core_web_sm")
    db = DocBin()
    # print(small_batch)
    for text, annotations in small_batch:
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        try:
            doc.ents = ents
            db.add(doc)
        except Exception as e:
            # print("Error: ", e, text, annotations)
            continue #skip the current iteration and continue with the next one
        # spaCyTrainData/test.txt
    db.to_disk("./spaCyTrainData/relativePromptsSampleDoc.spacy") #saves it as a spacy docbin file that can be loaded into a spacy model

if __name__ == "__main__":
    main()
