import json
import urllib.request
import json


def recursiveSearch(comboGraph, subGraph, key, rLevel, minWeight):
    """ Recursively search through a graph to find a subgraph based on weight and distance.
    This removes the subgraph from the original graph 

    Keyword arguments:
    comboGraph -- The graph to search (input)
    subGraph   -- The resulting graph (output)
    key        -- The key to search from
    rlevel     -- The recursive level to limit the size of the subgraph
    minWeight  -- The minimum necesary weight of an edge to add it to the subgraph
    """

    # If the vertex is in the graph
    if (key in comboGraph.keys()):
        # Move it from the main graph to the subgraph
        subGraph[key] = comboGraph.pop(key)
        # For all edges from that vertex
        for rKey in subGraph[key].keys():
            # If we haven't recursed too far and the edge is weighty enough
            if(rLevel > -1 and subGraph[key][rKey] >= minWeight):
                # Keep searching
                recursiveSearch(comboGraph, subGraph,
                                rKey, rLevel-1, minWeight)


if __name__ == "__main__":

    # Create an empty graph. Each key in this dict is a vertex. Each vertex is
    # represented as another dict. Each key in a vertex's dict is another vertex.
    # The weight of the edge is the value associated with that key
    comboGraph = dict({})

    # Load the JSON from the web
    with urllib.request.urlopen("https://sheets.googleapis.com/v4/spreadsheets/1JJo8MzkpuhfvsaKVFVlOoNymscCt-Aw-1sob2IhpwXY/values:batchGet?ranges=combos!A2:O&key=AIzaSyDzQ0jCf3teHnUK17ubaLaV6rcWf9ZjG5E") as url:
        data = json.loads(url.read().decode())
        # Pull out the array of combos (rows in the spreadsheet). This has cards, colors, conditions, and outcomes
        values = data['valueRanges'][0]['values']
        # For each combo
        for combo in values:
            # For each card in the combo (up to the first ten elements)
            for cardIdx in range(10):
                # If the card exists
                card1 = combo[cardIdx]
                if card1:
                    # If the card doesn't have a vertex in the graph yet
                    if card1 not in comboGraph.keys():
                        # Add the card to the graph by creating a dict in the dict for it
                        comboGraph[card1] = dict({})
                    # Now that the card is guaranteed to be in the graph, get the edges for this vertex
                    card1edges = comboGraph[card1]

                    # For each other card in the combo (first ten elements, if it exists)
                    for cardIdx2 in range(10):
                        if(cardIdx != cardIdx2 and combo[cardIdx2]):
                            card2 = combo[cardIdx2]

                            # If there is no edge between the two cards yet, create one with weight one
                            if card2 not in card1edges.keys():
                                card1edges[card2] = 1
                            else:
                                # Otherwise increment that edge's weight
                                card1edges[card2] = card1edges[card2] + 1

    # Now that the full graph is built, do a recursive search for all cards no
    # more than three edges of weight one away from Sliver Queen
    queenGraph = dict({})
    recursiveSearch(comboGraph, queenGraph, "Sliver Queen", 2, 1)

    # Write the graphviz for this graph
    with open("combo.gv", "w") as fout:
        fout.write("digraph {\n")
        # For each vertex
        for card1 in queenGraph.keys():
            # For each edge
            for card2 in queenGraph[card1].keys():
                # Each edge is bidirectional, so only draw it once with dir="both"
                if (card1 > card2):
                    fout.write("\"" + card1 + "\" -> \"" + card2 +
                               "\" [dir=\"both\" label = \"" + str(queenGraph[card1][card2]) + "\"]\n")
        fout.write("}\n")
