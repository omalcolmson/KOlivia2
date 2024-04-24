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
    # print("Testing model...")
    # text = "Mark my calendar as out of office from 3 pm to 5 pm on June 13th."
    # text = "Add an event to my calendar for 4 pm on April 25th to redecorate my bulletin board."
    # doc = nlp(text)
    # for ent in doc.ents:
    #     print(ent.text, ent.label_)

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

    Input: Mark my calendar as out of office from 3 pm to 5 pm on June 13th
    Output: 
    3 DATE_START
    5 pm on June PM_TIME_END
    13th DATE_START

    Commentary -> I think this is happening because the order of the entities in the examples are always the same. I think I need to go back and vary the order of the entities in the examples. 
    '''

    # Evaluating the saved model
    # loading the model
    # nlp = spacy.load("./spaCyModels/trained_test_model")

    # db = DocBin().from_disk("./spaCyTrainData/exactApptEval.spacy")

    # # Convert the DocBin to a list of Docs
    # docs = list(db.get_docs(nlp.vocab))

    # # Convert Docs to Examples
    # examples = []
    # for doc in docs:
    #     # Create an Example object
    #     example = Example.from_dict(doc, {"entities": doc.ents})
    #     examples.append(example)

    # # Evaluate the model using the examples
    # scores = nlp.evaluate(examples)
    # print("Precision:", scores["ents_p"])
    # print("Recall:", scores["ents_r"])
    # print("F1-score:", scores["ents_f"])

    '''
    Precision: 0.9998706338939198
    Recall: 1.0
    F1-score: 0.9999353127627919
    '''
    # loading the eval data from disk
    # doc_bin_file = "./spaCyTrainData/exactApptEval.spacy" 

    # #initializes an instance of the Corpus spacy class which we use to load the data into
    # eval_data = spacy.tokens.DocBin().from_disk(doc_bin_file)
    # # shuffle the data to add some randomness
    # # random.shuffle(eval_data)

    # # Convert the DocBin to spaCy examples
    # examples = []
    # for doc in eval_data.get_docs(nlp.vocab):
    #     for ent in doc.ents:
    #         spans = [{"start": ent.start_char, "end": ent.end_char, "label": ent.label_}]
    #         example = Example.from_dict(doc, {"entities": spans})
    #         examples.append(example)

    # # Print the first few examples to verify
    # #print(examples[:5])

    # # evaluate the model and print the results
    # scores = nlp.evaluate(examples)
    # print(scores)


if __name__ == "__main__":
    main()