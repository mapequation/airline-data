import argparse
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter, defaultdict
from random import random

paths = []
validationPaths = []
names = {}

def getName(id):
    # Use id as default value if not exist in names dict
    return names.get(id, id)

def readNames(name_input):
    print("Parse name input from {}...".format(name_input))
    with open(name_input, mode='r') as infile:
        dialect = csv.Sniffer().sniff(infile.readline())
        infile.seek(0)
        reader = csv.DictReader(infile, dialect=dialect)
        headers = reader.fieldnames
        print("Names header:", headers)
        for row in reader:
            names[row['Code']] = row['Description']
    print("Parsed {} names!".format(len(names)))


def parsePaths(filename, weight_threshold, split):
    print("Parse paths from {}...".format(filename))

    with open(filename, mode='r') as infile:
        rowNr = 0
        numPaths = 0
        numIgnoredByWeightThreshold = 0
        for row in infile:
            rowNr += 1
            if rowNr % 10000 == 0:
                print("Parsed {} rows...".format(rowNr))
            # if rowNr == 1:
            if row[0] == '*':
                continue
            numPaths += 1
            path = row.split()
            # print(path)
            weight = int(path[-1])
            if weight < weight_threshold:
                numIgnoredByWeightThreshold += 1
                continue
            if random() < split:
                validationPaths.append(row)
            else:
                paths.append(row)
    print("Done parsing {} paths from {} rows!".format(numPaths, rowNr))
    if weight_threshold > 0:
        print("  {} paths ignored by weight threshold".format(numIgnoredByWeightThreshold))
    if split > 0:
        print("  -> {} training paths saved".format(len(paths)))
        print("  -> {} validation paths saved".format(len(validationPaths)))
    else:
        print("  -> {} paths saved".format(len(paths)))

def writePaths(paths, outFilename):
    vertices = {}
    if len(names) > 0:
        print("Collecting vertices with names...")
        for p in paths:
            path = p.split()
            for v in path[:-1]:
                vertices[v] = getName(v)
        print("Found {} vertices!".format(len(vertices)))


    with open(outFilename, mode='w') as outfile:
        print("Writing {} paths to {}...".format(len(paths), outFilename))
        if len(vertices) > 0:
            outfile.write("*vertices {}\n".format(len(vertices)))
            for id,name in vertices.items():
                outfile.write("{} \"{}\"\n".format(id, name))
        outfile.write("*paths\n")
        for p in paths:
            # outfile.write("{}\n".format(p))
            outfile.write(p)
    print("Done!")

def run(inFilenames, outFilename, weight_threshold, split, name_input):
    t0, t1 = time.clock(), time.time()
    if name_input:
        readNames(name_input)

    for inFilename in inFilenames:
        parsePaths(inFilename, weight_threshold, split)
    
    if split > 0:
        name = outFilename.rsplit(".", maxsplit=1)[0]
        extension = outFilename.rsplit(".", maxsplit=1)[-1]
        outFilenameTraining = "{}_training.{}".format(name, extension)
        outFilenameValidation = "{}_validation.{}".format(name, extension)
        writePaths(paths, outFilenameTraining)
        writePaths(validationPaths, outFilenameValidation)
    else:
        writePaths(paths, outFilename)

def main(argv):
    parser = argparse.ArgumentParser(description='Filter paths.')
    parser.add_argument('input', nargs='+', help='input path files')
    parser.add_argument('output', help='output filename')
    parser.add_argument('--name-input', help='external csv file with names to add to the paths')
    parser.add_argument('-w', '--weight-threshold', type=float, help='Ignore paths with weight less than this threshold (default: 0.0)', default=0.0)
    parser.add_argument('-s', '--split', type=float, help='Split to training/validation set with fraction <s> (between 0 and 1) of paths to validation set (default: 0.0)', default=0.0)

    args = parser.parse_args()
    t0, t1 = time.clock(), time.time()
    print("==== Starting ====")
    print("  input: {}".format(args.input))
    print("  output: {}".format(args.output))
    print("  name_input: {}".format(args.name_input))
    print("  weight_threshold: {}".format(args.weight_threshold))
    print("  split: {}".format(args.split))
    
    run(args.input, args.output, args.weight_threshold, args.split, args.name_input)

    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:     {}".format(time.clock() - t0))
    print("Wall time:      {}".format(time.time() - t1))
    print("User mode time: {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:    {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))

if __name__ == "__main__":
   main(sys.argv[1:])


