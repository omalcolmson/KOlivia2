import random
import spacy
from spacy.tokens import DocBin
from spacy.training import Example

'''
Script for testing the spaCy model (really, to see if I know how to read documentation and can actually train the model correctly before doing it for real.)
'''

def main():
    print("Loading model...")
    nlp = spacy.blank("en") #loads blank model
    # nlp = spacy.load("en_core_web_trf") #loads the pretrained model
    # nlp = spacy.load("en_core_web_sm")

        # Add the entity recognizer to the pipeline if it doesn't exist
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
        new_labels = ["AM_TIME_START", "AM_TIME_END", "PM_TIME_START", "PM_TIME_END", "MILITARY_TIME_START", "MILITARY_TIME_END", "DATE_START", "DATE_END"]
        for label in new_labels:
            ner.add_label(label)

    # Load data from DocBin from disk
    print("Loading data...")
    db = DocBin().from_disk("/Users/olivi/OneDrive/Desktop/410/KOlivia2/spaCyTrainData/exactApptTrain.spacy")

    # Convert the DocBin to a list of Docs
    docs = list(db.get_docs(nlp.vocab))

    # Convert Docs to Examples
    print("Converting data to examples...")
    examples = []
    for doc in docs:
        entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        examples.append(Example.from_dict(doc, {"entities": entities}))

    # Train NER model using loaded data
    print("Training model...")
    nlp.begin_training()
    for i in range(10):
        random.shuffle(examples)
        for batch in spacy.util.minibatch(examples, size=8):
            nlp.update(batch)

    # Save the model to disk
    print("Saving model...")
    nlp.to_disk("./spaCyModels/trained_test_model")

    # Test the trained model
    print("Testing model...")
    text = "I have a doctor's appointment at 3:30 pm on May 15th."
    doc = nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)

if __name__ == "__main__":
    main()