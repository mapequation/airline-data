import argparse
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter, defaultdict

MKT_ID = "MKT_ID"
SEQ_NUM = "SEQ_NUM"
ORIGIN = "ORIGIN"
DEST = "DEST"

ngrams = Counter()
airports = Counter()
airportIndex = {}

def getName(filename):
    return filename.rsplit(".", maxsplit=1)[0]

def parseCsv(filename):
    print('Parse airline data from "{}"...'.format(filename))
    print("Aggregating bigrams by market id...")
    links = defaultdict(list)
    with open(filename, mode='r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        rowNr = 0
        for row in reader:
            rowNr += 1
            # print(row)
            mktId = row[MKT_ID]
            seqNr = row[SEQ_NUM]
            origin = row[ORIGIN]
            dest = row[DEST]
            # print("======", mktId, origin, dest)
            # links[itinId].append((itinId, mktId, sourceId, targetId))
            links[mktId].append((mktId, origin, dest))
            airports[origin] += 1
            airports[dest] += 1
            
            if rowNr % 100000 == 0:
                print("Processed {} rows...".format(rowNr))
    print("Done aggregating bigrams!")
    print("Indexing {} airports...".format(len(airports)))
    idx = 0
    for airport in airports:
        airportIndex[airport] = idx
        # print("Airport {}: {}, index: {}".format(airport, airports[airport], airportIndex[airport]))
        idx += 1
    print("Aggregate to unique ngrams...")
    for ngram in links.values():
        # ngrams["{} {}".format(ngram[0][1], " ".join([v[2] for v in ngram]))] += 1
        ngrams["{} {}".format(airportIndex[ngram[0][1]], " ".join([str(airportIndex[v[2]]) for v in ngram]))] += 1
    print("Done ")



def run(inputFilename, outputFilename):
    print('\n==== Starting ==== \n')
    t0, t1 = time.clock(), time.time()
    parseCsv(inputFilename)
    print('Done!')
    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:       {}".format(time.clock() - t0))
    print("Wall time:        {}".format(time.time() - t1))
    print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')
    print("Writing paths to {}...".format(outputFilename))
    with open(outputFilename, mode='w') as outfile:
        outfile.write("*paths\n")
        for ngram in ngrams:
            outfile.write("{} {}\n".format(ngram, ngrams[ngram]))
    print("Done!")
    


def main(argv):
    parser = argparse.ArgumentParser(description='Make paths from csv data.')
    parser.add_argument('input', help='input csv file')
    parser.add_argument('output', help='output paths file')

    args = parser.parse_args()
    run(args.input, args.output)

if __name__ == "__main__":
   main(sys.argv[1:])


