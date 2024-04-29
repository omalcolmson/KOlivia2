import random
import spacy
from spacy.tokens import DocBin
from spacy.training import Example

'''
Script for testing the spaCy model (really, to see if I know how to read documentation and can actually train the model correctly before doing it for real.)
'''

def main():
    # print("Loading model...")
    # nlp = spacy.blank("en") #loads blank model
    # # nlp = spacy.load("en_core_web_trf") #loads the pretrained model
    # # nlp = spacy.load("en_core_web_sm")

    #     # Add the entity recognizer to the pipeline if it doesn't exist
    # if "ner" not in nlp.pipe_names:
    #     ner = nlp.add_pipe("ner")
    #     new_labels = ["AM_TIME_START", "AM_TIME_END", "PM_TIME_START", "PM_TIME_END", "MILITARY_TIME_START", "MILITARY_TIME_END", "DATE_START", "DATE_END"]
    #     for label in new_labels:
    #         ner.add_label(label)

    # # Load data from DocBin from disk
    # print("Loading data...")
    # db = DocBin().from_disk("/Users/olivi/OneDrive/Desktop/410/KOlivia2/spaCyTrainData/exactApptTrain.spacy")

    # # Convert the DocBin to a list of Docs
    # docs = list(db.get_docs(nlp.vocab))

    # # Convert Docs to Examples
    # print("Converting data to examples...")
    # examples = []
    # for doc in docs:
    #     entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    #     examples.append(Example.from_dict(doc, {"entities": entities}))

    # # Train NER model using loaded data
    # print("Training model...")
    # nlp.begin_training()
    # for i in range(10):
    #     random.shuffle(examples)
    #     for batch in spacy.util.minibatch(examples, size=8):
    #         nlp.update(batch)

    # # Save the model to disk
    # print("Saving model...")
    # nlp.to_disk("./spaCyModels/trained_test_model")

    # # Test the trained model
    # print("Testing model...")
    # text = "I have a doctor's appointment at 3:30 pm on May 15th."
    # doc = nlp(text)
    # for ent in doc.ents:
    #     print(ent.text, ent.label_)

    trainer = spacy.load("./spaCyModels/trained_event_model") # load the trained model
    ner = trainer.get_pipe("ner") # get the NER model
    # ner.add_label("REASON")
    relative_labels = ["RELATIVE_DATE", "RELATIVE_TIME", "RELATIVE_DATE_TIME"]
    for label in relative_labels:
        ner.add_label(label)
    # Load data from DocBin from disk
    print("Loading data...")
    # db = DocBin().from_disk("/Users/olivi/OneDrive/Desktop/410/KOlivia2/spaCyTrainData/exactApptReasonTrain.spacy")
    db = DocBin().from_disk("/Users/olivi/OneDrive/Desktop/410/KOlivia2/spaCyTrainData/relativePromptsSampleDoc.spacy") #load relative prompts data


    # Convert the DocBin to a list of Docs
    docs = list(db.get_docs(trainer.vocab))

    # Convert Docs to Examples
    print("Converting data to examples...")
    examples = []
    for doc in docs:
        entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        examples.append(Example.from_dict(doc, {"entities": entities}))

    # Train NER model using loaded data
    print("Training model...")
    trainer.begin_training()
    for i in range(10):
        random.shuffle(examples)
        for batch in spacy.util.minibatch(examples, size=8):
            trainer.update(batch)

    # Save the model to disk
    print("Saving model...")
    # trainer.to_disk("./spaCyModels/trained_event_model") #saving as a new model to prevent overwriting the old one in case this doesn't work
    trainer.to_disk("./spaCyModels/trained_relative_model") #saving as a new model to prevent overwriting the old one in case this doesn't work

    # Test the trained model
    print("Testing model...")
    text = "Mark my calendar to go to work dinner from 3 pm to 5 pm on June 13th." #should perform the same as the previous model
    doc = trainer(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    print()
    text = "Mark my calendar in 30 mins from now to cry about my Networks exam." #not sure how it will react to minutes.. didn't include that in training data
    doc = trainer(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)

if __name__ == "__main__":
    main()