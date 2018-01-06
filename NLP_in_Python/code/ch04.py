# CSV Demo
>>> import csv
>>> input_file = open("lexicon.csv", "rb")
>>> for row in csv.reader(input_file):
... print row