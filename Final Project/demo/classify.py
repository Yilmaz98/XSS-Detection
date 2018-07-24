from argparse import ArgumentParser
from random import shuffle
import csv
from sklearn.naive_bayes import GaussianNB


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("dataset",help="The dataset file")
    parser.add_argument("model",help="The classifier model")

    return parser.parse_args()

def load_classes(dataset_file):

    classes={}
    f=open(dataset_file,"rb")
    csv_file=csv.reader(f,delimiter=",")

    for row in csvfile:
        klass,terms = row[0], row[1:]
        classes.setdefault(klass,[])
        classes[klass].append(terms)

    f.close()

    return classes

def split_dataset(classes,ratio):
    training_set={}
    test_set={}

    for klass in classes:
        sep=int(len(classes[klass]*ratio)

        shuffle(classes[klass])

        train,test=classes[klass][:sep],classes[klass][sep:]

        training_set[klass]=train
        test_set[klass]=test

    return training_set,test_set 


def main():
    args=get_arguments()

    classes= load_classes(args.dataset)
    train,test = split_dataset(classes, 0.6)
    classifier = GaussianNB()
    classifier.fit(train)
                accuracy,recall,f1=classifier.predict(test)

