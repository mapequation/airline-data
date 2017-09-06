import argparse
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter, defaultdict

# # inputName = 'data/2011_1_Coupon_paths_head.net'
# inputName = 'data/2011_1_Coupon_paths.net'
# # outputName = 'data/states.net'
# outputName = 'data/2011_1_Coupon_states.net'

stateNodes = Counter()
stateLinks = Counter()
intraLinks = defaultdict(Counter)
stateNodeIndex = {}

def getName(filename):
    return filename.rsplit(".", maxsplit=1)[0]

def getFilename(year, quarter):
    return "data/{}_{}_Coupon_paths.net".format(year, quarter)

def parsePaths(filename, layer):
    print('Parse paths data from "{}" and generate layer state nodes...'.format(filename))
    # links = defaultdict(list)
    links = intraLinks[layer]
    with open(filename, mode='r') as infile:
        rowNr = 0
        for row in infile:
            rowNr += 1
            if rowNr == 1:
                continue
            path = row.split()
            # print(path)
            prevNode = path[0]
            endIdx = len(path) - 1
            weight = int(path[-1])
            for idx, node in enumerate(path):
                if idx == 0:
                    continue
                if idx == endIdx:
                    break
                
                links[(prevNode, node)] += weight
                prevNode = node
            if rowNr % 100000 == 0:
                print("Processed {} rows...".format(rowNr))
    print("Done parsing paths!")

def writeMultilayer(filename):
    print("Writing multilayer network to {}...".format(filename))
    numLayers = len(intraLinks)
    with open(filename, mode='w') as outfile:
        print("Writing {} layers of nodes...".format(numLayers))
        layerIndex = 0
        outfile.write("*Intra\n")
        outfile.write("# layer node node weight\n")
        for layer, links in intraLinks.items():
            # layer node node weight
            # print("layer {} (index {})...".format(layer, layerIndex))
            for link, weight in links.items():
                # print(link, weight)
                outfile.write("{} {} {} {}\n".format(layerIndex, link[0], link[1], weight))
            layerIndex += 1        
        # print("Writing {} multilayer links...".format(len(stateLinks)))
    print("Done!")


def run(years):
    print('\n==== Starting ==== \n')
    t0, t1 = time.clock(), time.time()
    for year in years:
        for quarter in [1,2,3,4]:
            layer = "{}_{}".format(year, quarter)
            parsePaths(getFilename(year, quarter), layer)
    
    outname = "data/multilayer_{}_{}_states.net".format(years[0], years[-1])
    writeMultilayer(outname)
    print('Done!')
    print('MEMORY USAGE     : {} MB'.format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000))
    print('{} seconds process time, {} seconds wall time'.format(time.clock() - t0, time.time() - t1))
    # write_time_file(outfile, str(time.clock() - t0) + ' seconds process time\n' + str(time.time() - t1) + ' seconds wall time')
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')

def test(filename):
    print('\n==== Starting ==== \n')
    t0, t1 = time.clock(), time.time()
    
    parsePaths(filename, 0)
    
    outname = "{}_mulitlayer_test.net".format(getName(filename))
    writeMultilayer(outname)
    print('Done!')
    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:       {}".format(time.clock() - t0))
    print("Wall time:        {}".format(time.time() - t1))
    print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')


def main(argv):
    parser = argparse.ArgumentParser(description='Paths to multilayer states format.')
    parser.add_argument('input', nargs='?', default='', help='input')
    parser.add_argument('-y', '--years', nargs='+', type=int, help='years')

    args = parser.parse_args()
    # print(args.input)
    # print(args.years)
    # test(args.input)
    run(args.years)

if __name__ == "__main__":
   main(sys.argv[1:])


