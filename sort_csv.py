
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter

PREZIPPED = True
# PREZIPPED = False
infilename = 'data/2011_1_Coupon.csv'
# infilename = 'data/test/unsorted_head21.csv'
outfilename = 'data/2011_1_Coupon_sorted.csv'

if PREZIPPED:
    # Prezipped download
    ITIN_ID = "ItinID"
    MKT_ID = "MktID"
    ORIGIN_AIRPORT_ID = "OriginAirportID"
    DEST_AIRPORT_ID = "DestAirportID"
    YEAR = "Year"
    QUARTER = "Quarter"
else:
    # Selected download
    ITIN_ID = "ITIN_ID"
    MKT_ID = "MKT_ID"
    ORIGIN_AIRPORT_ID = "ORIGIN_AIRPORT_ID"
    DEST_AIRPORT_ID = "DEST_AIRPORT_ID"
    YEAR = "YEAR"
    QUARTER = "QUARTER"


def sortCsv(filename):
    print('Parse airline data from "{}"...'.format(filename))
    with open(filename, mode='r') as infile, open(outfilename,"w") as outfile:
        dialect = csv.Sniffer().sniff(infile.readline())
        infile.seek(0)
        reader = csv.DictReader(infile, dialect=dialect)

        headers = reader.fieldnames

        print("headers: {}".format(headers))

        writer = csv.DictWriter(outfile, delimiter=',', fieldnames = headers)
        # writer = csv.DictWriter(outfile, delimiter=',', fieldnames = fieldnames, quoting=csv.QUOTE_NONE, quotechar='\t', escapechar='')
        writer.writeheader()

        # sort= sorted(reader,key=operator.itemgetter(7), reverse= True)
        sorted_rows = sorted(reader, key=lambda row: row[MKT_ID])

        for row in sorted_rows:
            writer.writerow(row)


def run():
    print('\n==== Starting ==== \n')
    t0, t1 = time.clock(), time.time()
    sortCsv(infilename)
    print('Done!')
    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:       {}".format(time.clock() - t0))
    print("Wall time:        {}".format(time.time() - t1))
    print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')

def test():
    print('Testing... done!')


def usage():
    print('{} -i <input_csv> -o <output_csv>'.format(sys.argv[0]))


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hio",["help", "input", "output"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    # inputPath = ""
    # outputPath = ""
    # for opt, arg in opts:
    #     if opt in ("-h", "--help"):
    #         usage()
    #         sys.exit()
    #     elif opt in ("--input"):
    #         inputPath = arg
    #     elif opt in ("--output"):
    #         outputPath = arg
    # print("input = {}, output = {}".format(inputPath, outputPath))
    # usage()
    run()

if __name__ == "__main__":
   main(sys.argv[1:])


