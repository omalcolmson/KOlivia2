import random
import spacy
from spacy.tokens import DocBin
from spacy.training import Example
'''
Script for testing if the spacy model saved ;-;
'''

def main():
    # load our saved model
    nlp = spacy.load("./spaCyModels/trained_test_model")

    # Test the trained model
    print("Testing model...")
    text = "Mark my calendar as out of office from 3 pm to 5 pm on June 13th."
    doc = nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)

    '''
    Input: Mark my calendar as OOO from 3 pm to 5 pm on June 13th.
    Output: 
    OOO from 3 pm DATE_START -> ERROR, should not be PM_TIME_START
    5 pm PM_TIME_END
    June 13th. DATE_START

    Iput: Mark my calendar as out of office from 3 pm to 5 pm on June 13th.
    Output:
    3 pm PM_TIME_START
    5 pm on June PM_TIME_END -> ERROR, should be 5 pm PM_TIME_END, June shouldn't have been split up from 13th
    13th DATE_START
    . PM_TIME_END -> ERROR, not sure why it's labeling the period as the time. Maybe because none of the training data had a period at the end?
    '''
if __name__ == "__main__":
    main()