# web-mining-community-detection
Web mining project: Detect communities relevant to elonmusk on Twitter, using snap.py's Girvan-Newman algorithm.

Run:

	$ python main.py -i <input-edges-file> -l <max-graph-level> -s <start-node-label> -n <max_nodes>

where input file format is similar to file sample-data/user_pairs.txt:

	decodethefirm-CarsThatThink
	decodethefirm-MikeSpectorWSJ
	decodethefirm-claireeboston
	decodethefirm-ryanfelton
	decodethefirm-Telluride
	decodethefirm-elonmusk
	decodethefirm-DunneAutomotive
	decodethefirm-NAIASDetroit
	cdelancray-cdelancray
	cdelancray-Joi
	cdelancray-rodneyabrooks

Example:

	$ python main.py -i edge.txt -l 6 -s elonmusk -n 1000

Result: a graph file in gexf format in output directory, each node has a integer community attributes.

Use Gephi to visualize graph.

### References:

- [snap.py](https://snap.stanford.edu/snappy/)

- [Girvan-Newman algorithm](https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm)

- [networkx](https://networkx.github.io/documentation/stable/)

- [Gephi](https://gephi.org/users/)