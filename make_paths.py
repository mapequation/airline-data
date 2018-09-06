import argparse
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter, defaultdict, namedtuple

Bigram = namedtuple('Bigram', ['sourceId', 'targetId', 'itinId', 'mktId', 'seqNum'])

# Prezipped download
ITIN_ID = "ItinID"
MKT_ID = "MktID"
SEQ_NUM = "SeqNum"
ORIGIN_AIRPORT_ID = "OriginAirportID"
DEST_AIRPORT_ID = "DestAirportID"
YEAR = "Year"
QUARTER = "Quarter"

# ITIN_ID = "ITIN_ID"
# MKT_ID = "MKT_ID"
# SEQ_NUM = "SEQ_NUM"
# ORIGIN_AIRPORT_ID = "ORIGIN_AIRPORT_ID"
# DEST_AIRPORT_ID = "DEST_AIRPORT_ID"
# YEAR = "YEAR"
# QUARTER = "QUARTER"

def useNonPrezippedFormat():
    # Selected download
    ITIN_ID = "ITIN_ID"
    MKT_ID = "MKT_ID"
    SEQ_NUM = "SEQ_NUM"
    ORIGIN_AIRPORT_ID = "ORIGIN_AIRPORT_ID"
    DEST_AIRPORT_ID = "DEST_AIRPORT_ID"
    YEAR = "YEAR"
    QUARTER = "QUARTER"

ngrams = Counter()

def getName(filename):
    return filename.rsplit(".", maxsplit=1)[0]

def isPrezipped(filename):
    return not getName(filename).endswith("_min")

def parseCsv(filename):
    print('Parse airline data from "{}"...'.format(filename))
    print("Group bigrams by itinierary id...")
    tripIdToBigrams = defaultdict(list)
    if not isPrezipped(filename):
        print("Use non-prezipped file format")
        useNonPrezippedFormat()
    with open(filename, mode='r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        rowNr = 0
        for row in reader:
            rowNr += 1
            # print(row)
            itinId = row[ITIN_ID]
            mktId = row[MKT_ID]
            seqNum = int(row[SEQ_NUM])
            sourceId = row[ORIGIN_AIRPORT_ID]
            targetId = row[DEST_AIRPORT_ID]
            # print("======", itinId, sourceId, targetId)
            bigrams = tripIdToBigrams[itinId]
            bigrams.append(Bigram(sourceId, targetId, itinId, mktId, seqNum))
            # bigrams.append((sourceId, targetId, itinId, mktId, seqNum))
            
            if rowNr % 100000 == 0:
                print("Processed {} rows...".format(rowNr))
    print("Done grouping bigrams to {} trips!".format(len(tripIdToBigrams)))
    print("Aggregate to unique ngrams...")
    for bigrams in tripIdToBigrams.values():
        # sort bigrams on sequence number
        # bigrams.sort(key=lambda tup: tup[4])  # sorts in place by seqNum
        bigrams.sort(key=lambda tup: tup.seqNum)
        # assert a correct sequence order
        for n, bigram in enumerate(bigrams, start=1):
            # if n != bigram[4]:
            if n != bigram.seqNum:
                sys.exit("Bigram {} has not correct seqNum in bigrams {}".format(bigram, bigrams))
            # targetId of previous bigram should be sourceId for current bigram
            # if n > 1 and bigrams[n-2][1] != bigrams[n-1][0]:
            if n > 1 and bigrams[n-2].targetId != bigrams[n-1].sourceId:
                sys.exit("Bigram {} doesn't connect to previous bigrams {}".format(bigram, bigrams))
        # Get all connected by using targetId of all bigrams and prepend sourceId of first
        ngrams["{} {}".format(bigrams[0].sourceId, " ".join([bigram.targetId for bigram in bigrams]))] += 1
        # ngrams["{} {}".format(bigrams[0][0], " ".join([bigram[1] for bigram in bigrams]))] += 1
    print("Done ")



def writeCsv(docs, filename, fieldnames):
    print('Write to "{}"...'.format(filename))
    with open(filename, mode='w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames = fieldnames, quoting=csv.QUOTE_NONE, quotechar='\t', escapechar='')
        writer.writeheader()
        for docid, doc in docs.items():
            writer.writerow(doc)


def run(filename, outputFilename):
    print('\n==== Starting ==== \n')
    t0, t1 = time.clock(), time.time()
    parseCsv(filename)
    print('Done!')
    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:       {}".format(time.clock() - t0))
    print("Wall time:        {}".format(time.time() - t1))
    print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')
    if not outputFilename:
        outputFilename = "{}_paths.net".format(getName(filename))
    print("Writing paths to {}...".format(outputFilename))
    with open(outputFilename, mode='w') as outfile:
        outfile.write("*paths\n")
        for ngram in ngrams:
            outfile.write("{} {}\n".format(ngram, ngrams[ngram]))
    print("Done!")
    


def main(argv):
    parser = argparse.ArgumentParser(description='Make paths from csv data.')
    parser.add_argument('input', help='input csv file')
    parser.add_argument('output', nargs='?', help='optional filename for output path data instead of default based on input')

    args = parser.parse_args()
    run(args.input, args.output)

if __name__ == "__main__":
   main(sys.argv[1:])


