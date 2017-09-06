import argparse
import math
import sys
# import csv, json
import resource, time
# from time import gmtime, strftime
from collections import Counter, defaultdict

def entropy(P):
    H = 0.0
    for p in P:
        if p > 0 and p < 1:
            H -= p * math.log2(p)
    # return -sum(0 if p is 0 else p * math.log2(p) for p in P)
    return H

def run(filename):
    nodesPerModule = defaultdict(list)
    modulesPerNode = defaultdict(list)

    with open(filename, 'r') as infile:
        for line in infile:
            if line[0] == '#':
                continue
            row = line.split()
            node = int(row[0])
            module = int(row[1])
            flow = float(row[2])
            nodesPerModule[module].append((node, flow))
            modulesPerNode[node].append(module)
    
    moduleFlow = []
    numModules = len(nodesPerModule)
    numPhysicalNodes = len(modulesPerNode)
    for module, nodes in nodesPerModule.items():
        moduleFlow.append(sum(n[1] for n in nodes))
    H = entropy(moduleFlow)
    numModuleAssignments = 0
    for node, modules in modulesPerNode.items():
        numModuleAssignments += len(modules)
    numModuleAssignments /= numPhysicalNodes
    print("numModules:", numModules, "entropy:", H, "perplexity:", math.pow(2, H),
        "numModuleAssignments:", numModuleAssignments)



def main(argv):
    # print('\n==== Starting ==== \n')
    # t0, t1 = time.clock(), time.time()

    parser = argparse.ArgumentParser(description='Calculate cluster statistics.')
    # parser.add_argument('-i', '--input', nargs=1, type=argparse.FileType('r'), required=True)
    parser.add_argument('input', help='input cluster file')

    args = parser.parse_args()
    run(args.input)


    # print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    # print("Clock time:       {}".format(time.clock() - t0))
    # print("Wall time:        {}".format(time.time() - t1))
    # print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    # print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))

if __name__ == "__main__":
   main(sys.argv[1:])