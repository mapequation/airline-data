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
stateNodeIndex = {}

def getName(filename):
    return filename.rsplit(".", maxsplit=1)[0]

def getNameWithoutPath(filename):
    return filename.rsplit(".", maxsplit=1)[0].split('/')[-1]

def getFilename(year, quarter):
    return "data/{}_{}_Coupon_paths.net".format(year, quarter)

def parsePathToFirstOrderStates(path):
    endIdx = len(path) - 1
    weight = int(path[-1])

    prevStateNode = path[0]
    stateNodes[prevStateNode] += 1
    for idx, node in enumerate(path):
        # if idx < 1:
        #     continue
        if idx == endIdx:
            break
        stateNode = path[idx]
        stateNodes[stateNode] += 1
        stateLinks[(prevStateNode,stateNode)] += weight
        prevStateNode = stateNode

def parsePathToSecondOrderStates(path):
    endIdx = len(path) - 1
    weight = int(path[-1])
    prevStateNode = (path[0], path[1])
    stateNodes[prevStateNode] += 1
    for idx, node in enumerate(path):
        if idx < 1:
            continue
        if idx == endIdx:
            break
        stateNode = (path[idx-1], path[idx])
        stateNodes[stateNode] += 1
        stateLinks[(prevStateNode,stateNode)] += weight
        prevStateNode = stateNode

def parsePathToThirdOrderState(path):
    endIdx = len(path) - 1
    weight = int(path[-1])
    prevStateNode = (path[0], path[1], path[2])
    stateNodes[prevStateNode] += 1
    for idx, node in enumerate(path):
        if idx < 2:
            continue
        if idx == endIdx:
            break
        stateNode = (path[idx-2], path[idx-1], path[idx])
        stateNodes[stateNode] += 1
        stateLinks[(prevStateNode,stateNode)] += weight
        prevStateNode = stateNode

pathParsers = {
    1: parsePathToFirstOrderStates,
    2: parsePathToSecondOrderStates,
    3: parsePathToThirdOrderState,
}

def parsePathsToStates(filename, order, count_threshold):
    print("Parse paths data from {} and generate state nodes of order {}...".format(filename, order))

    if order not in [1,2,3]:
        sys.exit("Order not supported: {}".format(order))
    
    parser = pathParsers[order]
    
    with open(filename, mode='r') as infile:
        rowNr = 0
        numIgnoredByCountThreshold = 0
        numIgnoredByLengthThreshold = 0
        for row in infile:
            rowNr += 1
            if rowNr % 100000 == 0:
                print("Processed {} rows...".format(rowNr))
            if rowNr == 1:
                continue
            path = row.split()
            # print(path)
            endIdx = len(path) - 1
            weight = int(path[-1])
            if weight < count_threshold:
                numIgnoredByCountThreshold += 1
                continue
            # Skip paths shorter than maximum used
            if endIdx <= 3:
                numIgnoredByLengthThreshold += 1
                continue
            parser(path)
    print("Done parsing {} paths!".format(rowNr - 1))
    print("  Number of paths ignored by count threshold:", numIgnoredByCountThreshold)
    print("  Number of paths ignored by length threshold:", numIgnoredByLengthThreshold)


def writeFirstOrderNetwork(filename):
    print("Writing first order network to {}...".format(filename))
    numStateNodes = len(stateNodes)
    with open(filename, mode='w') as outfile:
        print("Writing {} state nodes...".format(numStateNodes))
        outfile.write("*vertices {}\n".format(numStateNodes))
        idx = 0
        for stateNode, count in stateNodes.items():
            stateNodeIndex[stateNode] = idx
            outfile.write("{} \"{}\"\n".format(idx, stateNode))
            idx += 1        
        print("Writing {} state links...".format(len(stateLinks)))
        outfile.write("*arcs\n")
        for stateLink, count in stateLinks.items():
            # print(stateLink, count)
            outfile.write("{} {}\n".format(stateNodeIndex[stateLink[0]], stateNodeIndex[stateLink[1]]))
    print("Done!")

def writeFirstOrderStates(filename):
    print("Writing states to {}...".format(filename))
    numStateNodes = len(stateNodes)
    with open(filename, mode='w') as outfile:
        print("Writing {} state nodes...".format(numStateNodes))
        outfile.write("*states {}\n".format(numStateNodes))
        idx = 0
        for stateNode, count in stateNodes.items():
            stateNodeIndex[stateNode] = idx
            outfile.write("{} {} \"{}\"\n".format(idx, stateNode, stateNode))
            idx += 1        
        print("Writing {} state links...".format(len(stateLinks)))
        outfile.write("*links\n")
        for stateLink, weight in stateLinks.items():
            # print(stateLink, weight)
            outfile.write("{} {} {}\n".format(stateNodeIndex[stateLink[0]], stateNodeIndex[stateLink[1]], weight))
    print("Done!")

def writeSecondOrderStates(filename):
    print("Writing states to {}...".format(filename))
    numStateNodes = len(stateNodes)
    with open(filename, mode='w') as outfile:
        print("Writing {} state nodes...".format(numStateNodes))
        outfile.write("*states {}\n".format(numStateNodes))
        idx = 0
        for stateNode, count in stateNodes.items():
            stateNodeIndex[stateNode] = idx
            outfile.write("{} {} \"{} {}\"\n".format(idx, stateNode[1], stateNode[0], stateNode[1]))
            idx += 1        
        print("Writing {} state links...".format(len(stateLinks)))
        outfile.write("*links\n")
        for stateLink, weight in stateLinks.items():
            # print(stateLink, weight)
            outfile.write("{} {} {}\n".format(stateNodeIndex[stateLink[0]], stateNodeIndex[stateLink[1]], weight))
    print("Done!")

def writeThirdOrderStates(filename):
    print("Writing third order states to {}...".format(filename))
    numStateNodes = len(stateNodes)
    with open(filename, mode='w') as outfile:
        print("Writing {} state nodes...".format(numStateNodes))
        outfile.write("*states {}\n".format(numStateNodes))
        idx = 0
        for stateNode, count in stateNodes.items():
            stateNodeIndex[stateNode] = idx
            outfile.write("{} {} \"{} {} {}\"\n".format(idx, stateNode[2], stateNode[0], stateNode[1], stateNode[2]))
            idx += 1        
        print("Writing {} state links...".format(len(stateLinks)))
        outfile.write("*links\n")
        for stateLink, weight in stateLinks.items():
            # print(stateLink, weight)
            outfile.write("{} {} {}\n".format(stateNodeIndex[stateLink[0]], stateNodeIndex[stateLink[1]], weight))
    print("Done!")

def writeCsv(docs, filename, fieldnames):
    print('Write to "{}"...'.format(filename))
    with open(filename, mode='w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames = fieldnames, quoting=csv.QUOTE_NONE, quotechar='\t', escapechar='')
        writer.writeheader()
        for docid, doc in docs.items():
            writer.writerow(doc)

def runSingle(pathsFilename, order):
    parsePathsToStates(pathsFilename, order)
    
    outname = "data/{}_states_{}.net".format(getNameWithoutPath(pathsFilename), order)
    if order == 1:
        # writeFirstOrderNetwork("{}_{}_pajek.net".format(year, quartersString))
        writeFirstOrderStates(outname)
    elif order == 2:
        writeSecondOrderStates(outname)
    elif order == 3:
        writeThirdOrderStates(outname)

def run(year, order, quarters, count_threshold):
    quartersString = "".join(map(str, quarters))
    for quarter in quarters:
        print("Collecting paths from quarter {}...".format(quarter))
        pathsFilename = getFilename(year, quarter)
        parsePathsToStates(pathsFilename, order, count_threshold)

    outname = "data/{}_{}_states_{}.net".format(year, quartersString, order)
    if order == 1:
        # writeFirstOrderNetwork("{}_{}_pajek.net".format(year, quartersString))
        writeFirstOrderStates(outname)
    elif order == 2:
        writeSecondOrderStates(outname)
    elif order == 3:
        writeThirdOrderStates(outname)
    print('\n== Finished at', strftime("%Y-%m-%d %H:%M:%S", gmtime()), '== \n')


def main(argv):
    parser = argparse.ArgumentParser(description='Paths to states format.')
    parser.add_argument('input', nargs='?', help='optional input paths file to use instead of from args')
    parser.add_argument('-o', '--order', type=int, help='markov order (default: 1)', default=1)
    parser.add_argument('-y', '--year', required=True, type=int, help='year', default=1)
    parser.add_argument('-q', '--quarter', required=True, help='quarter (1-4), use multiple times for many quarters', type=int, action='append')
    parser.add_argument('-c', '--count-threshold', type=int, help='Ignore paths with count less than this threshold (default: 2)', default=2)

    args = parser.parse_args()
    t0, t1 = time.clock(), time.time()
    print("==== Starting ====")
    print("  order: {}".format(args.order))
    print("  year: {}".format(args.year))
    print("  quarter: {}".format(args.quarter))
    print("  count_threshold: {}".format(args.count_threshold))
    if args.input:
        runSingle(args.input, args.order)
    else:
        run(args.year, args.order, args.quarter, args.count_threshold)

    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:     {}".format(time.clock() - t0))
    print("Wall time:      {}".format(time.time() - t1))
    print("User mode time: {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:    {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))

if __name__ == "__main__":
   main(sys.argv[1:])


