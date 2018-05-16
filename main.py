import snap
import random
import pickle
import sys
import getopt
import networkx as nx
import matplotlib.pyplot as plt

def main(argv):
	# ------------------------------------------------------------------------------
	# Constants
	TEMP_DIR = 'temp'
	OUT_DIR = 'output'
	SAMPLE_DATA_DIR = 'sample-data'

	# ------------------------------------------------------------------------------
	# TODO: Get arguments
	input_user_pairs_file = '%s/user_pairs.txt' % SAMPLE_DATA_DIR; # input data
	output_graph_image_file = '%s/default.png' % OUT_DIR # output graph image
	max_level = 2 # graph max level
	start_node = 'elonmusk'
	max_nodes = 1000 # max number of edges

	try:
		opts, args = getopt.getopt(argv, 'hi:o:l:s:n:', ['ifile=', 'ofile=', 'max_level=', 'start_node=', '=max_edges'])
	except getopt.GetoptError:
		print('main.py -i <input-file> -o <output-image-file> -l <max-graph-level> -s <start-node-label> -n <max_nodes>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('main.py -i <input-file> -o <output-image-file> -l <max-graph-level> -s <start-node-label> -n <max_nodes>')
			sys.exit()
		elif opt in ('-i', '--ifile'):
			input_user_pairs_file = arg
		elif opt in ('-o', '--ofile'):
			output_graph_image_file = arg
		elif opt in ('-l', '--max_level'):
			max_level = int(arg)
		elif opt in ('-n', '--max_nodes'):
			max_nodes = int(arg)
		elif opt in ('-s', '--start_node'):
			start_node = arg

	print('')
	print('Max level = %d' % (max_level))
	print('Max nodes = %d' % (max_nodes))
	print('Start node = %s' % (start_node))
	print('-----------------------')

	# ------------------------------------------------------------------------------
	# Read user pairs into a list of edges, and users to dictionaries
	label_id_map = {} # map username to id
	id_label_map = {} # map id to username
	pairs = [] # edge list
	n_users = 0 # number of users

	with open(input_user_pairs_file, 'r') as f:
		lines = f.readlines()
		for line in lines:
			# Split line
			line_arr = line.strip().split('-')
			if len(line_arr) < 2:
				break

			# Nodes of edge
			label_source = line_arr[0]
			label_target = line_arr[1]

			# Add users
			if not label_id_map.has_key(label_source):
				label_id_map[label_source] = n_users
				id_label_map[n_users] = label_source
				n_users += 1

			if not label_id_map.has_key(label_target):
				label_id_map[label_target] = n_users
				id_label_map[n_users] = label_target
				n_users += 1

			# Add pair
			pairs.append([label_id_map[label_source], label_id_map[label_target]])


	# ## Save user dictionary
	# save_pickle(label_id_map, '%s/label_id.pkl' % TEMP_DIR)
	# label_id_map = load_pickle('%s/label_id.pkl' % TEMP_DIR)

	# save_pickle(id_label_map, '%s/id_label.pkl' % TEMP_DIR)
	# id_label_map = load_pickle('%s/id_label.pkl' % TEMP_DIR)

	## Save edges
	save_pickle(pairs, '%s/edges.pkl' % TEMP_DIR)
	pairs = load_pickle('%s/edges.pkl' % TEMP_DIR)


	# ------------------------------------------------------------------------------
	# Create a graph from users and user pairs
	## Adjacient list graph
	### Init list
	adjacient_list = {}
	for node_id in id_label_map.keys():
		adjacient_list[node_id] = []

	### Build list
	for pair in pairs:
		x = pair[0]
		y = pair[1]
		adjacient_list[x].append(y)
		adjacient_list[y].append(x)

	### Save adjacent list
	save_pickle(adjacient_list, '%s/adj_list.pkl' % TEMP_DIR)
	adjacient_list = load_pickle('%s/adj_list.pkl' % TEMP_DIR)

	## Get start node
	if not label_id_map.has_key(start_node):
		print('Error: Start node does not exist.')
		sys.exit(2)

	start_node_id = label_id_map[start_node]

	## Nodes in each level
	levels = []

	## Level 0
	levels.append(set([start_node_id]))

	## Upper levels
	for i in range(1, max_level + 1):
		others = [set([])]
		for node_id in levels[i - 1]:
			others.append(set(adjacient_list[node_id]))
		this_level = set.union(*others).difference(*[levels[j] for j in range(i)])
		levels.append(this_level)

	## Reduced nodes
	print('Number of nodes in each level:')
	for i in range(len(levels)):
		print('Level %d: %d' % (i, len(levels[i])))
	print('-----------------------')

	reduced_node_ids = set([]) # reduced node ids
	reduced_id_label_map = {}
	reduced_label_id_map = {}
	n_nodes = 0 # number of nodes

	for i in range(max_level + 1):
		for node_id in levels[i]:
			# Add to nodes
			# reduced_node_ids.add(node_id)
			reduced_node_ids.add(n_nodes)
			reduced_label_id_map[id_label_map[node_id]] = n_nodes
			reduced_id_label_map[n_nodes] = id_label_map[node_id]

			# Nodes limit
			n_nodes += 1
			if n_nodes == max_nodes:
				break

	## Reduced adjacent list
	reduced_adj_list = {} # reduced adjacient list
	n_edges = 0

	for node_id in reduced_node_ids:
		new_adjacient_list = []
		for nid in adjacient_list[node_id]:
			label = id_label_map[nid]
			if reduced_label_id_map.has_key(label):
				new_adjacient_list.append(reduced_label_id_map[label])

		# # Adjacient list
		# reduced_adj_list[node_id] = set.intersection(*[set(new_adjacient_list),\
		# 		reduced_node_ids])
		
		reduced_adj_list[node_id] = new_adjacient_list

		n_edges += len(reduced_adj_list[node_id])

	

	## Save reduced
	save_pickle(reduced_node_ids, '%s/reduced_node_ids_lv%d.pkl' % (TEMP_DIR, max_level))
	reduced_node_ids = load_pickle('%s/reduced_node_ids_lv%d.pkl' % (TEMP_DIR, max_level))

	save_pickle(reduced_adj_list, '%s/reduced_adj_list_lv%d.pkl' % (TEMP_DIR, max_level))
	reduced_adj_list = load_pickle('%s/reduced_adj_list_lv%d.pkl' % (TEMP_DIR, max_level))

	save_pickle(reduced_label_id_map, '%s/reduced_label_id_map_lv%d.pkl' % (TEMP_DIR, max_level))
	reduced_label_id_map = load_pickle('%s/reduced_label_id_map_lv%d.pkl' % (TEMP_DIR, max_level))

	save_pickle(reduced_id_label_map, '%s/reduced_id_label_map_lv%d.pkl' % (TEMP_DIR, max_level))
	reduced_id_label_map = load_pickle('%s/reduced_id_label_map_lv%d.pkl' % (TEMP_DIR, max_level))

	print('After reducing:')
	print('Number of nodes: %d' % (len(reduced_node_ids)))
	print('Number of edges: %d' % (n_edges))
	print('-----------------------')	

	# ------------------------------------------------------------------------------
	# Create snap graph
	print('Step create graph')

	## Graph for community detection
	UG = create_graph(reduced_node_ids, reduced_adj_list, id_label_map)

	# for node in UG.Nodes():
	# 	print(node.GetId())
	# for edge in UG.Edges():
	# 	print(edge.GetId())

	## Graph for drawing
	UG2 = create_graph(reduced_node_ids, reduced_adj_list, id_label_map)

	# FIn2 = snap.TFIn('%s/UG2.graph' % TEMP_DIR)
	# UG2 = snap.TUNGraph.Load(FIn2)

	print('...\nDONE step create graph')
	print('-----------------------')

	# ------------------------------------------------------------------------------
	# Run Given-Newman algorithm
	## Comunities
	print('Step detect communities')

	CmtyV = snap.TCnComV()
	modularity = snap.CommunityGirvanNewman(UG, CmtyV) 
	
	## Map node id to community
	id_community_map = {} 
	i = 0
	for Cmty in CmtyV:
		for NI in Cmty:
			id_community_map[NI] = i
		i += 1

	print('...\nDONE step detect community')
	print('-----------------------')

	print(reduced_node_ids)
	print(id_community_map)

	# # ------------------------------------------------------------------------------
	# # Use communities to color the nodes
	# print('Step color')

	# ## Colors map
	# colors = {}

	# for Cmty in CmtyV:
	# 	# Random color
	# 	r = lambda: random.randint(0,255)
	# 	color = '#%02X%02X%02X' % (r(),r(),r())
	# 	print("Community: ")
	# 	comms = ''
	# 	for NI in Cmty:
	# 		comms += str(NI) + ' '
	# 		colors[NI] = color
	# 	print(comms)

	# print("The modularity of the network is %f" % modularity)
	# print('-----------------------')

	# ## Save color
	# save_pickle(colors, '%s/colors_lv%d.pkl' % (TEMP_DIR, max_level))
	# colors = load_pickle('%s/colors_lv%d.pkl' % (TEMP_DIR, max_level))

	# # ------------------------------------------------------------------------------
	# # Draw and save graph using GViz
	# ## Draw
	# print('Step draw')

	# ### Get color hash
	# NIdColorH = colors_object(colors, reduced_node_ids)

	# # snap.DrawGViz(UG2, snap.gvlNeato, "%s/Neato_color_lv%d.png" % (OUT_DIR, max_level), "Elonmusk", True, NIdColorH)
	# # snap.DrawGViz(UG2, snap.gvlTwopi, "%s/Twopi_color_lv%d.png" % (OUT_DIR, max_level), "Elonmusk", True, NIdColorH)
	
	# ## Draw with colors
	# snap.DrawGViz(UG2, snap.gvlSfdp, "%s/Sfdp_color_lv%d.png" % (OUT_DIR, max_level), "Elonmusk", True, NIdColorH)
	
	# # ### Draw without colors
	# # snap.DrawGViz(UG2, snap.gvlSfdp, "%s/Sfdp_color_lv%d.png" % (OUT_DIR, max_level), "Elonmusk", True)
	
	# print('...\nDONE step draw')
	# print('-----------------------')



	# ------------------------------------------------------------------------------
	# Log
	print('INFO:')
	print('\nNode - id:')
	for nid in reduced_node_ids:
		print('%d - %s' % (nid, reduced_id_label_map[nid]))
	print('\nStart node ID: %d' % (reduced_label_id_map[start_node]))
	print('-----------------------')


	# ------------------------------------------------------------------------------
	# Save to gexf networkx
	## Create graph
	G = nx.Graph()

	for nid in reduced_adj_list.keys():
		# Add node and label
		G.add_node(nid, label=reduced_id_label_map[nid], community=id_community_map[nid])
		
		# Add edges
		adj_list = reduced_adj_list[nid]
		for adj_id in adj_list:
			G.add_edge(nid, adj_id)

	## Write to file
	nx.write_gexf(G, '%s/elonmusk_reduced_lv%d.gexf' % (OUT_DIR, max_level))

	return 0;	


# Save a object to a pickle file
def save_pickle(obj, filepath):
	with open(filepath, 'wb') as f:
		pickle.dump(obj, f)

# Load a object from a pickle file
def load_pickle(filepath):
	with open(filepath, 'rb') as f:
		return pickle.load(f)

# Create snap graph
def create_graph(node_ids, adjacient_list, id_label_map):
	# Create new graph
	UG = snap.TUNGraph.New()

	# # Labels
	# labels = snap.TIntStrH()
	# for nid in node_ids:
	# 	labels[nid] = id_label_map[nid]

	# Add nodes
	for nid in node_ids:
		UG.AddNode(int(nid))

	# Add edges
	for nid in adjacient_list.keys():
		adj_list = adjacient_list[nid]
		for adj_nid in adj_list:
			UG.AddEdge(int(nid), int(adj_nid))

	return UG

# Get color hash for snap graph
def colors_object(colors_dic, node_ids):
	NIdColorH = snap.TIntStrH()

	for nid in node_ids:
		NIdColorH[nid] = colors_dic[nid]

	return NIdColorH


if __name__ == '__main__':
	main(sys.argv[1:])

