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
def genAptTypeD(reason, startDateStr, endDateStr):
    typeD = [
        f"Mark my calendar as out of office starting on {startDateStr} to {endDateStr}",
        f"Schedule my vacation from {startDateStr} to {endDateStr}",
        f"From {startDateStr} to {endDateStr}, block off time in my calendar for {reason}",
        f"Add an event to my calendar from {startDateStr} until {endDateStr}",
        f"Block off time from {startDateStr} to {endDateStr} to {reason}",
        f"Put an event on my calendar from {startDateStr} to {endDateStr}",
        f"Create an event from {startDateStr} to {endDateStr} to {reason}",
        f"Block off my calendar from {startDateStr} to {endDateStr}",
        f"Starting on {startDateStr} to {endDateStr}, put an event on my calendar for {reason}",
        f"I will be out of office from {startDateStr} until {endDateStr}",
        f"Block off time in my calendar from {startDateStr} to {endDateStr} for {reason}",
        f"Put my trip from {startDateStr} to {endDateStr} on my calendar",
    ]
    return random.choice(typeD)

def genAptTypeC(singleDate, reason, timeStart, timeEnd):
    typeC = [
        f"Mark my calendar for the {singleDate} from {timeStart} to {timeEnd} for {reason}",
        f"Schedule a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Add an event to my calendar for {reason} on {singleDate} starting at {timeStart} and ending at {timeEnd}",
        f"Block off time for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Set up a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Put {reason} on my calendar for {singleDate} from {timeStart} to {timeEnd}",
        f"Remind me on {singleDate} from {timeStart} to {timeEnd} to {reason}",
        f"Pencil in {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Arrange a meeting to {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Book a meeting for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Create an event for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"Block off my calendar for {reason} on {singleDate} from {timeStart} to {timeEnd}",
        f"On {singleDate} from {timeStart} to {timeEnd}, schedule a meeting for {reason}",
    ]
    return random.choice(typeC)

def genAptTypeB(singleDate, reason, singleTime):
    typeB = [
        f"Mark my calendar for {singleDate} at {singleTime} for {reason}",
        f"Schedule a meeting for {reason} on {singleDate} at {singleTime}",
        f"Add an event to my calendar for {reason} on {singleDate} starting at {singleTime}",
        f"Block off time to {reason} on {singleDate} at {singleTime}",
        f"Set up a meeting for {reason} on {singleDate} at {singleTime}",
        f"Put {reason} on my calendar for {singleDate} at {singleTime}",
        f"Remind me on {singleDate} at {singleTime} to {reason}",
        f"Pencil in {reason} on {singleDate} at {singleTime}",
        f"Arrange a meeting to {reason} on {singleDate} at {singleTime}",
        f"Book a meeting for {reason} on {singleDate} at {singleTime}",
        f"Create an event for {reason} on {singleDate} at {singleTime}",
        f"Block off my calendar for {reason} on {singleDate} at {singleTime}",
        f"On {singleDate} at {singleTime}, schedule a meeting for {reason}",
    ]
    return random.choice(typeB)

def genAptTypeA(singleDate, reason):
    typeA = [
        f"Mark my calendar for {singleDate} for {reason}",
        f"Mark my calendar for {reason} on {singleDate}",
        f"Schedule an appointment for {reason} on {singleDate}",
        f"Schedule a meeting for {reason} on {singleDate}",
        f"Add an event to my calendar for {reason} on {singleDate}",
        f"Block off time for {reason} on {singleDate}",
        f"Set up a meeting for {reason} on {singleDate}",
        f"Put {reason} on my calendar for {singleDate}",
        f"Remind me on {singleDate} to {reason}",
        f"Pencil in {reason} on {singleDate}",
        f"Arrange a meeting to {reason} on {singleDate}",
        f"Book a meeting with {reason} on {singleDate}",
        f"Create an event for {reason} on {singleDate}",
        f"Block off my calendar for {reason} on {singleDate}",
        f"On {singleDate}, schedule a meeting to {reason}",
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

    Prompt type int mapping:
    0 -> exact single date
    1 -> exact single time
    2 -> time period
    3 -> date period

    training_data = [
    ("Tokyo Tower is 333m tall.", [(0, 11, "BUILDING")]),
    ]
    '''
    #TODO: need to consider if we should handle relative times and dates and if those should be generated separately

    data = []
    # read in the csv file

    # COLS: Text, Label
    singleDatesDF = pd.read_csv("RawTrainData/exactDatesData.csv", index_col=0)
    # COLS: Start_Date, Start_Label, End_Date, End_Label
    datePeriodsDF = pd.read_csv("RawTrainData/datePeriodsData.csv", index_col=0)
    # COLS: Text, Label
    singleTimesDF = pd.read_csv("RawTrainData/exactTimesData.csv", index_col=0)
    # COLS: Start_Time, Start_Label, End_Time, End_Label
    timePeriodsDF = pd.read_csv("RawTrainData/timePeriodsData.csv", index_col=0)

    for i in range(200): 
        singleDateTuple = selectRandomDF(singleDatesDF)
        datePeriodTuple = selectRandomDF(datePeriodsDF)
        singleTimeTuple = selectRandomDF(singleTimesDF)
        timePeriodTuple = selectRandomDF(timePeriodsDF)
        
    # events/appts with 1 date no times
        singleDate = singleDateTuple[0][0]
        singleDateLabel = singleDateTuple[0][1]
        reason = random.choice(pc.actions) #randomly select a reason for the event from actions list
        aptA = genAptTypeA(singleDate, reason)
        sample = createAnnotation(aptA, [(singleDate, singleDateLabel)])
        # print(sample)
        data.append(sample)

        # events/appts with 1 date and 1 time
        singleTime = singleTimeTuple[0][0]
        singleTimeLabel = singleTimeTuple[0][1]
        aptB = genAptTypeB(singleDate, reason, singleTime)
        sample = createAnnotation(aptB, [(singleDate, singleDateLabel), (singleTime, singleTimeLabel)])
        # print(sample)
        data.append(sample)

        # # events/appts with 1 date and a start and end time
        # print(timePeriodTuple)
        timeStartTuple = timePeriodTuple[0]
        timeEndTuple = timePeriodTuple[1]
        timeStart = timeStartTuple[0]
        timeStartLabel = timeStartTuple[1]
        timeEnd = timeEndTuple[0]
        timeEndLabel = timeEndTuple[1]
        aptC = genAptTypeC(singleDate, reason, timeStart, timeEnd)
        sample = createAnnotation(aptC, [(singleDate, singleDateLabel), (timeStart, timeStartLabel), (timeEnd, timeEndLabel)])
        # print(sample)
        data.append(sample)

        # events/appts with 2 dates and no times
        startDate = datePeriodTuple[0]
        endDate = datePeriodTuple[1]
        startDateStr = startDate[0]
        startDateLabel = startDate[1]
        endDateStr = endDate[0]
        endDateLabel = endDate[1]
        aptD = genAptTypeD(reason, startDateStr, endDateStr)
        sample = createAnnotation(aptD, [(startDateStr, startDateLabel), (endDateStr, endDateLabel)])
        data.append(sample)

    return data


def main():

    # testing with a small batch
    small_batch = genPrompts() #small list of prompts
    listofDicts = listToListDicts(small_batch)

    with open("PreparedTrainData/small_train.json", "w") as f:
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
    db.to_disk("./spaCyTrainData/exactApptTrain.spacy") #saves it as a spacy docbin file that can be loaded into a spacy model

if __name__ == "__main__":
    main()
