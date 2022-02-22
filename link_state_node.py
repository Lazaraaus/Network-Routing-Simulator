from simulator.node import Node
import json
import math

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # KEYS (Node1, Node2) 2-tuple
        # Change key to frozenset so we don't have to double updates
        self.link_latency = {} # Dict to hold the weights of the links
        self.edges_sq_num = {} # Dict to hold the sequence # for each link
    # Return a string
    def __str__(self):
        return str(self.id) #"Rewrite this function to define your node dump printout"
    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # CASE 1: Delete Link
        if latency == -1 and neighbor in self.neighbors:
            # Remove from Neighbors List
            self.neighbors.remove(neighbor)            
            # Remove edges
            self.link_latency.pop((self.id, neighbor))
            self.link_latency.pop((neighbor, self.id))
            # Construct MSG To Neighbors [link source, link dest, latency, timestamp:seq_num]
            msg_src_node = self.id
            msg = json.dumps([self.id, neighbor, latency, self.get_time(), msg_src_node])
            # Send MSG
            self.send_to_neighbors(msg)
        else:
            # Init Link State Alg - Flood Network 
            # Get the previous cost of this link
            prev_cost = self.link_latency.get((self.id, neighbor))
            # Update costs with new latency            
            self.link_latency.update({(self.id,neighbor):latency})  #[(self.id, neighbor)] = latency
            self.link_latency.update({(neighbor, self.id):latency}) #[(neighbor, self.id)] = latency
            # Update sq_nums with new timestamps
            self.edges_sq_num.update({(self.id, neighbor):self.get_time()}) #[(self.id, neighbor)] = self.get_time()
            self.edges_sq_num.update({(neighbor, self.id):self.get_time()}) #[(neighbor, self.id)] = self.get_time()
            
            # Check if neighbor is new to the network
            if neighbor not in self.neighbors:
                # If so, add to neighbors
                self.neighbors.append(neighbor)
                # Broadcast new link to new neighbor to all neighbors
                msg_src_node = self.id    
                broadcast = json.dumps([self.id, neighbor, latency, self.get_time(), msg_src_node])
                self.send_to_neighbors(broadcast)
                # Loop and share link with individual nodes in Neighbors
                for node_1, node_2 in self.link_latency.keys():
                    # Update latencies, seq_nums for links
                    link_latency = self.link_latency.get((node_1, node_2))
                    link_sq_num = self.edges_sq_num.get((node_1, node_2))
                    msg_src_node = self.id
                    broadcast = json.dumps([node_1, node_2, link_latency, link_sq_num, msg_src_node])
                    # Broadcast new info to neighbors
                    self.send_to_neighbor(neighbor, broadcast)

            # Neighbor already in Neighbors
            else:
                # Check if latency needs to be updated on link
                if prev_cost != latency:
                    # Update seq_nums 
                    self.edges_sq_num.update({(self.id, neighbor):self.get_time()}) #[(self.id, neighbor)] = self.get_time()
                    self.edges_sq_num.update({(neighbor, self.id):self.get_time()}) #[(neighbor, self.id)] = self.get_time()
                    # Construct Msg
                    msg_src_node = self.id
                    broadcast = json.dumps([self.id, neighbor, latency, self.get_time(), msg_src_node])
                    # Send Msg
                    self.send_to_neighbors(broadcast)
    # Fill in this function
    def process_incoming_routing_message(self, m):
        # Deconstruct Msg 
        node_1, node_2, latency, seq_num, msg_src_node_in = json.loads(m)
        # CASE 1: THERE IS NO SEQ_NUM for (node_1, node_2)
        try:
            old_seq_num = self.edges_sq_num[(node_1, node_2)] 

        except Exception as e:
            # Doesn't exist, Init Info
            self.edges_sq_num.update({(node_1, node_2):seq_num}) #[(node_1, node_2)] = seq_num
            self.edges_sq_num.update({(node_2, node_1):seq_num}) #[(node_2, node_1)] = seq_num
            self.link_latency.update({(node_1, node_2):latency}) #[(node_1, node_2)] = latency
            self.link_latency.update({(node_2, node_1): latency})
            # Check if latency is -1 
            if latency == -1:
                # If so, pop edges
                self.link_latency.pop((node_1, node_2))
                self.link_latency.pop((node_2, node_1)) 
            # Construct msg
            msg_src_node_out = self.id
            broadcast = json.dumps([node_1, node_2, latency, seq_num, msg_src_node_out])
            # Send msg
            # Prevent infinite cycle
            for neighbor in self.neighbors:
                # Check if neighbor is not sender
                if neighbor != msg_src_node_in:
                    # If not, broadcast 
                    self.send_to_neighbor(neighbor, broadcast)
            

        # CASE 2: THERE IS: Compare to see which node has older info
        else:
            # CASE 2.A: message is new
            # print(f"The type of old_seq_num is : {type(old_seq_num)}")
            # print(f"The type of seq_num is: {type(seq_num)}")
            if seq_num > old_seq_num: # Check sequence against each other
                # Update latency, seq_num, broadcast
                self.edges_sq_num.update({(node_1, node_2) : seq_num})
                self.edges_sq_num.update({(node_2, node_1) : seq_num}) #[(node_2, node_1)] = seq_num
                self.link_latency.update({(node_1, node_2) : latency}) #[(node_1, node_2)] = latency
                self.link_latency.update({(node_2, node_1) : latency}) #[(node_2, node_1)] = latency
                # Check if latency is -1
                if latency == -1:
                    # Pop latencies for the link
                    self.link_latency.pop((node_1, node_2))
                    self.link_latency.pop((node_2, node_1))
                # Construct Msg
                msg_src_node_out = self.id
                broadcast = json.dumps([node_1, node_2, latency, seq_num, msg_src_node_out])
                for neighbor in self.neighbors:
                    # Check if neighbor is not sender
                    if neighbor != msg_src_node_in:
                        # broacast
                        self.send_to_neighbor(neighbor, broadcast)
                 
            # CASE 2.B: THIS NODE HAS RECENT INFO
            elif seq_num < old_seq_num: # Check sequence numbers against each other
                    # Back Prop info to network
                    # Just Build Updated Broadcast Message and Send to msg_src_node
                    seq_num = self.edges_sq_num.get((node_1, node_2))
                    latency = self.link_latency.get((node_1, node_2))
                    msg_src_node_out = self.id
                    broadcast = json.dumps([node_1, node_2, latency, seq_num, msg_src_node_out])
                    # Send to node with outdate info
                    self.send_to_neighbor(msg_src_node_in, broadcast)
                    return
    #############################################
    # Helper Funcs for Dijkstra's/get_next_hop()#
    #############################################
    # Get all the nodes in the network topology
    def get_nodes(self):
        list_of_nodes = []
        # Loop through all Nodes
        for node_1, node_2 in self.link_latency.keys():
            # Check if already in list
            if node_1 not in list_of_nodes:
                # If not, add to list
                list_of_nodes.append(node_1)
            # Same for node_2
            if node_2 not in list_of_nodes:
                list_of_nodes.append(node_2)
        # Return
        return list_of_nodes
    # Get all neighbors of a node in the network topology
    def get_neighbors(self, src_node):
        list_of_neighbors = []
        # loop through all nodes
        for node_1, node_2 in self.link_latency.keys():
            # Check if node_1 is the src_node and the other end node isn't in the list
            if node_1 == src_node and node_2 not in list_of_neighbors:
                # If so, add the end node
                list_of_neighbors.append(node_2)
            # Same for node_2
            if node_2 == src_node and node_1 not in list_of_neighbors:
                list_of_neighbors.append(node_1)
        # Return
        return list_of_neighbors
    # Sort a list of node objects based on a cost dict
    def sort_nodes(self, node, costs):
        return costs[node]
    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        ##################Dijkstra's Pseudocode###################
        # Step 1: Find the cheapest node (latency-wise)          #
        # Step 2: Update the costs of the neighbors of the node  #
        # Step 3: Repeat until you've visited every node         #
        # Step 4: Calc the final path                            #
        ##########################################################

        # Init Dijkstra's : lowest cost node, parent nodes, etc       
        cost_of_nodes = {}
        parent_nodes = {}
        # Get list of nodes in the network
        list_of_nodes = self.get_nodes()
        # Loop through all nodes
        for node in list_of_nodes:
            # Init cost/parent dicts for each node
            cost_of_nodes[node] = math.inf
            parent_nodes[node] = -1
        # Set cost of the destination node to 0
        cost_of_nodes[destination] = 0
        # loop through destination nodes neighbors
        for dest_neighbor in self.get_neighbors(destination):
            # Update Cost
            cost_of_nodes[dest_neighbor] = self.link_latency.get((dest_neighbor, destination))
            # Update parent nodes
            parent_nodes[dest_neighbor] = destination
        # Remove Destination
        list_of_nodes.remove(destination)
        # Sort List
        list_of_nodes.sort(key=lambda node: cost_of_nodes[node])

        # Start Dijkstra's 
        while list_of_nodes: 
            min_cost = math.inf
            min_node = list_of_nodes[0]
            # Loop through all vertices
            for node in list_of_nodes:
                # Check if node has a lower cost than min_cost
                if cost_of_nodes[node] < min_cost:
                    min_cost = cost_of_nodes[node]
                    min_node = node
            # Remove min node from list
            list_of_nodes.remove(min_node)

            # Loop through neighbors of min_node
            list_of_min_node_neighbors = self.get_neighbors(min_node)
            for neighbor in list_of_min_node_neighbors:
                # Check if we haven't remove neighbor AKA pathway still viable
                if neighbor in list_of_nodes:
                    # Get cost for the edge
                    new_cost = min_cost + self.link_latency.get((min_node, neighbor))
                    # Check if less than the cost of old path
                    if new_cost < cost_of_nodes[neighbor]:
                        # If so, update cost and path
                        cost_of_nodes[neighbor] = new_cost
                        parent_nodes[neighbor] = min_node

        # Return the penultimate node on the pathway to the destination node
        return parent_nodes.get(self.id)
