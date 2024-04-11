# TODOs

## spaCy NER Model

### Data Generation/Preprocessing

- [ ] more formats with varying syntaxes need to be added to create a more robust training corpus (currently only have a couple formats that vary the form and order of how dates and times are featured in sentences)
- [ ] add checks for time and date period generators to prevent them from creating tuples of the same times/dates or invalid pairings (e.g., end date occurs before start date)
- [ ] want to add reason label for the calendar requests (will be helpful for later when creating actual events)
- [ ] add periods to the end of requests and other punctuation to the requests
- [ ] run `runTimeTrain.py` to generate a larger corpus of text
- [ ] need to generate training data for relative dates and times 

