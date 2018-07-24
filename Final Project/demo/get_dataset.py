import re
import os
from os.path import join
import csv
from argparse import ArgumentParser
 
def get_arguments():
    parser = ArgumentParser()
 
    parser.add_argument("dataset", help="Path to the dataset")
    parser.add_argument("output", help="Name of the training file")
 
    return parser.parse_args()
     
def tokenize(text):
    """Split the documents into a list of terms"""
    terms = re.findall(r'\w+', text)
 
    terms = [term for term in terms
             if not term.isdigit()]
 
    return terms
 
def main():
    args = get_arguments()
 
    dataset_path = args.dataset
    dataset_file = args.output
 
    f = open(dataset_file, "wb")
    csv_file = csv.writer(f, delimiter=",")
 
    for dirname in os.listdir(dataset_path):
        klass = dirname
        classpath = join(dataset_path, dirname)
        for dirpath, dirnames, filenames in os.walk(classpath):
            for filename in filenames:
                filepath = join(dirpath, filename)
                with open(filepath, "r") as f:
                    contents= ''.join(f.readlines())
                    terms = tokenize(contents)
                    terms.insert(0, klass)
                    csv_file.writerow(terms)
     
    f.close()
     
if __name__ == "__main__":
    main()
