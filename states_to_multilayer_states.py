import argparse
import csv, json
import sys, getopt
import resource, time
from time import gmtime, strftime
from collections import Counter, defaultdict
import re
import networkx as nx

stateNodes = Counter()
stateLinks = Counter()
stateNodeIndex = {}
graphs = []
outDegreePerNode = defaultdict(float)
outDegreePerNodePerLayer = {}
multiStateNameToStateId = {}

def parseStates(filename):
    """ Parse states network with format
    *states
    # stateId physId "name"
    1 5 "1 5"
    2 5 "2 5"
    *links
    # fromStateId toStateId
    1 2
    """
    graphId = len(graphs)
    g = nx.DiGraph(graphId=graphId, outDegree=0)
    graphs.append(g)
    stateIdToName = {}
    outDegree = defaultdict(float)
    outDegreePerNodePerLayer[graphId] = outDegree
    with open(filename, mode='r') as infile:
        lineNr = 0
        isStates = False
        isLinks = False
        reState = re.compile(r'(\d+) (\d+) "(.+)"')
        for line in infile:
            if line[0] == '#':
                continue
            if isLinks:
                link = line.split()
                # print("link:", link)
                # g.add_edge(int(link[0]), int(link[1]), weight=float(link[2]))
                sourceId, targetId, weight = int(link[0]), int(link[1]), float(link[2])
                # sourceId = int(link[0])
                # targetId = int(link[1])
                # weight = float(link[2])
                g.add_edge(stateIdToName[sourceId], stateIdToName[targetId], weight=weight)
                g.graph['outDegree'] += weight
                outDegreePerNode[stateIdToName[sourceId]] += weight
                outDegree[stateIdToName[sourceId]] += weight
            elif isStates:
                if line.startswith("*links"):
                    isLinks = True
                    print("Parsing links...")
                    continue
                m = reState.match(line)
                if not m:
                    print("Line not matching a state node: '{}'".format(line))
                    sys.exit(1)
                stateId, physId, name = int(m.group(1)), int(m.group(2)), m.group(3)
                stateIdToName[stateId] = name
                # print("state node {} {}, name: {}".format(m.group(1), m.group(2), m.group(3)))
                # Index node by name
                g.add_node(name, stateId=stateId, physId=physId, name=name, graphId=graphId)
            else:
                if line.startswith("*states"):
                    print("Parsing state nodes...")
                    isStates = True
            lineNr += 1
            if lineNr % 10000 == 0:
                print("Processed {} rows...".format(lineNr))
    print("Done parsing state network with {} state nodes and {} links!".format(g.number_of_nodes(), g.number_of_edges()))
    # print("Nodes:", g.nodes(data=True))
    # print("Edges:", g.edges(data=True))


def generateMultilayerNetwork(relaxRate):
    print("Generate multilayer network from {} state networks...".format(len(graphs)))
    mg = nx.DiGraph(numLayers=len(graphs))
    multiStateIndex = 0
    for g1 in graphs:
        layer1 = g1.graph['graphId']
        print("Processing source layer {} with {} nodes...".format(layer1, g1.number_of_nodes()))
        nodeCount = 0
        for n1, d1 in g1.nodes_iter(data=True):
            # print("  Node {}, data: {}".format(n1, d1))
            multiSourceName = "{} {}".format(layer1, d1['name'])
            mg.add_node(multiSourceName, stateId=multiStateIndex, physId=d1['physId'])
            multiStateNameToStateId[multiSourceName] = multiStateIndex
            multiStateIndex += 1

            nodeCount += 1
            if nodeCount % 1000 == 0:
                print("  Processed {} nodes...".format(nodeCount))
            # if outDegreePerNodePerLayer[layer1][n1] == 0.0:
            #     continue
            for g2 in graphs:
                layer2 = g2.graph['graphId']
                isIntra = layer2 == layer1
                # outDegree2 = g2.out_degree(n1, weight='weight')
                # print("  -> layer {}, outDegree: {}/{}".format(layer2, outDegreePerNodePerLayer[layer2][n1], outDegreePerNode[n1]))

                if outDegreePerNode[n1] == 0.0:
                    continue
                linkWeightNormalizationFactor = relaxRate / outDegreePerNode[n1]
                if (isIntra):
                    if outDegreePerNodePerLayer[layer1][n1] == 0.0:
                        continue
                    linkWeightNormalizationFactor += (1.0 - relaxRate) / outDegreePerNodePerLayer[layer1][n1]
                for src2,tgt2,weight2 in g2.edges_iter(n1, data='weight'):
                    multiTargetName = "{} {}".format(layer2, tgt2)
                    multiWeight = linkWeightNormalizationFactor * weight2
                    mg.add_edge(multiSourceName, multiTargetName, weight=multiWeight)
                    # print("    -> multi edge: {} -> {}, weight: {}".format(multiSourceName, multiTargetName, multiWeight))
                
    
    print("Done!")
    # print("Nodes:", mg.nodes(data=True))
    # print("Edges:", mg.edges(data=True))
    return mg


def writeMultilayerStateNetwork(network, outFilename):
    """ Write network to outFilename """
    numStateNodes = network.number_of_nodes()
    numLinks = network.number_of_edges()
    with open(outFilename, mode='w') as outfile:
        print("Writing state network with {} state nodes and {} links to {}...".format(numStateNodes, numLinks, outFilename))
        outfile.write("*states {}\n".format(numStateNodes))
        for n, d in network.nodes_iter(data=True):
            outfile.write("{} {} \"{}\"\n".format(multiStateNameToStateId[n], d['physId'], n))
        outfile.write("*links {}\n".format(numLinks))
        for src, tgt, weight in network.edges_iter(data='weight'):
            outfile.write("{} {} {}\n".format(multiStateNameToStateId[src], multiStateNameToStateId[tgt], weight))
    print("Done!")



def run(inFilenames, outFilename, relaxRate):
    t0, t1 = time.clock(), time.time()
    for inFilename in inFilenames:
        print("Collecting states from {}...".format(inFilename))
        parseStates(inFilename)
    
    network = generateMultilayerNetwork(relaxRate)

    writeMultilayerStateNetwork(network, outFilename)


def main(argv):
    parser = argparse.ArgumentParser(description='Join states to multilayer states')
    parser.add_argument('input', nargs='+', help='input states files')
    parser.add_argument('output', help='output filename')
    parser.add_argument('-r', '--relax-rate', type=float, default=0.15, help='Multilayer relax rate')
    
    args = parser.parse_args()
    t0, t1 = time.clock(), time.time()
    print("==== Starting ====")
    print("  input: {}".format(args.input))
    print("  output: {}".format(args.output))
    print("  relax-rate: {}".format(args.relax_rate))

    run(args.input, args.output, args.relax_rate)

    print("Done!")
    print("Max memory usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6))
    print("Clock time:       {}".format(time.clock() - t0))
    print("Wall time:        {}".format(time.time() - t1))
    print("User mode time:   {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_utime))
    print("System time:      {}".format(resource.getrusage(resource.RUSAGE_SELF).ru_stime))


if __name__ == "__main__":
   main(sys.argv[1:])


