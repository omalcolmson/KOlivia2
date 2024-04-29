import genTimeDateData as gtt #used to be called gentimetrain hence gtt
import pandas as pd
'''
Script simply for running genTimeTrain.py

Separating the function calls to a this file is helpful as the length of genTimeTrain.py grows longer and for debugging purposes. 
'''
def main():
    # GENERATE EXACT TIMES --------------------------
    # exactTimes = gtt.genExactTimes()
    # df = pd.DataFrame(exactTimes, columns=['Text', 'Label'])
    # df.to_csv("RawTrainData/exactTimesData.csv", index=True)

    # GENERATE EXACT DATES --------------------------
    # exactDates = gtt.genExactDates()
    # df = pd.DataFrame(exactDates, columns=['Text', 'Label'])
    # df.to_csv("RawTrainData/exactDatesData.csv", index=True)

    # GENERATE TIME PERIODS --------------------------
    # timePeriods = gtt.genExactTimePeriods()
    # df = pd.DataFrame(timePeriods, columns=['Start', 'End'])
    # df[['Start_Time', 'Start_Label']] = df['Start'].apply(lambda x: pd.Series(x))
    # df[['End_Time', 'End_Label']] = df['End'].apply(lambda x: pd.Series(x))
    # df.drop(columns=['Start', 'End'], inplace=True)
    # df.to_csv("RawTrainData/timePeriodsData.csv", index=True)
    

    # GENERATE DATE PERIODS --------------------------
    # datePeriods = gtt.genDatePeriods()
    # df = pd.DataFrame(datePeriods, columns=['Start', 'End'])
    # df[['Start_Date', 'Start_Label']] = df['Start'].apply(lambda x: pd.Series(x))
    # df[['End_Date', 'End_Label']] = df['End'].apply(lambda x: pd.Series(x))
    # df.drop(columns=['Start', 'End'], inplace=True)
    # df.to_csv("RawTrainData/datePeriodsData.csv", index=True)

    
    # GENERATE RELATIVE DATES --------------------------
    # relativeDatePeriods = gtt.genRelativeDates()
    # df = pd.DataFrame(relativeDatePeriods, columns=['Text', 'Label'])
    # df.to_csv("RawTrainData/relativeDatePeriodsData.csv", index=True)

    # GENERATE RELATIVE TIMES --------------------------
    relativeTimePeriods = gtt.genRelativeTimes()
    df = pd.DataFrame(relativeTimePeriods, columns=['Text', 'Label'])
    df.to_csv("RawTrainData/relativeTimePeriodsData.csv", index=True)


    # pass

if __name__ == "__main__":
    main()