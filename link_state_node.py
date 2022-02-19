from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # KEYS (Node1, Node2) 2-tuple
        self.all_edges = {}
        self.edges_sq_num = {}

    # Return a string
    def __str__(self):
        return str(self.id) #"Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # Delete Link
        if latency == -1 and neighbor in self.neighbors:
            # Remove from Neighbors List
            self.neighbors.remove(neighbor)            
            # Remove edges
            self.all_edges.pop((self.id, neighbor))
            self.all_edges.pop((neighbor, self.id))
            # Construct MSG To Neighbors [link source, link dest, latency, timestamp:seq_num]
            msg_src_node = self.id
            msg = json.dumps([self.id, neighbor, latency, self.get_time(), msg_src_node])
            # Send MSG
            self.send_to_neighbors(msg)
        else:
            # Init Link State Alg
            prev_cost = self.all_edges[(self.id, neighbor)]
            # Update costs with new latency            
            self.all_edges[(self.id, neighbor)] = latency
            self.all_edges[(neighbor, self.id)] = latency
            # Update sq_nums with new timestamps
            self.edges_sq_num[(self.id, neighbor)] = self.get_time()
            self.edges_sq_num[(neighbor, self.id)] = self.get_time()
            
            # Check if neighbor is new to the network
            if neighbor not in self.neighbors:
                # Add to neighbors
                self.neighbors.append(neighbor)
                # Do we need to send a msg -- YES
                msg_src_node = self.id    
                broadcast = json.dumps([self.id, neighbor, latency, self.get_time(), msg_src_node])
                self.send_to_neighbors(broadcast)
                # Loop and share link with individual nodes in Neighbors
                for node_1, node_2 in self.all_edges.keys():
                    link_latency = self.all_edges[(node_1, node_2)]
                    link_sq_num = self.edges_sq_num[(node_1, node_2)]
                    msg_src_node = self.id
                    broadcast = json.dumps([node_1, node_2, link_latency, link_sq_num, msg_src_node])
                    self.send_to_neighbor(neighbor, broadcast)

            # Neighbor already in Neighbors
            else:
                # Check if latency was updated on link
                if prev_cost != latency:
                    # Update seq_nums 
                    self.edges_sq_num[(self.id, neighbor)] = self.get_time()
                    self.edges_sq_num[(neighbor, self.id)] = self.get_time()
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
            self.edges_sq_num[(node_1, node_2)] = seq_num
            self.edges_sq_num[(node_2, node_1)] = seq_num
            self.all_edges[(node_1, node_2)] = latency
            self.all_edges[(node_1, node_2)] = latency
            # Check if latency is -1 
            if latency == -1:
                # If so, pop edges
                self.all_edges.pop((node_1, node_2))
                self.all_edges.pop((node_2, node_1)) 
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
            return

        # CASE 2: THERE IS: Compare to see which node has older info
        else:
            # Check old_seq_num against seq_num
            if seq_num > old_seq_num:
                # Update latency, seq_num, broadcast
                self.edges_seq_num[(node_1, node_2)] = seq_num
                self.edges_sq_num[(node_2, node_1)] = seq_num
                self.all_edges[(node_1, node_2)] = latency
                self.all_edges[(node_2, node_1)] = latency
                # Check if latency is -1
                if latency == -1:
                    # Pop latencies for the link
                    self.all_edges.pop((node_1, node_2))
                    self.all_edges.pop((node_2, node_1))
                # Construct Msg
                msg_src_node_out = self.id
                broadcast = json.dumps([node_1, node_2, latency, seq_num, msg_src_node_out])
                for neighbor in self.neighbors:
                    # Check if neighbor is not sender
                    if neighbor != msg_src_node_in:
                        # broacast
                        self.send_to_neighbor(neighbor, broadcast)
                return
        
            # CASE 3: THIS NODE HAS RECENT INFO - Back Propagate to Sender Node
            else:
                # Just Build Updated Broadcast Message and Send to msg_src_node
                seq_num = self.edges_sq_num[(node_1, node_2)]
                latency = self.all_edges[(node_1, node_2)]
                msg_src_node_out = self.id
                broadcast = json.dumps([node_1, node_2, latency, seq_num, msg_src_node_out])
                # Send to node with outdate info
                self.send_to_neighbor(msg_src_node_in, broadcast)
                return

    # Helper Funcs for Dijkstra's/get_next_hop()
    def get_nodes():
        list_of_nodes = []
        # Loop through all Nodes
        for node_1, node_2 in self.all_edges.keys():
            # Check if already in list
            if node_1 not in list_of_nodes:
                # If not, add to list
                list_of_nodes.append(node_1)
            if node_2 not in list_of_nodes:
                list_of_nodes.append(node_2)
        # Return
        return list_of_nodes
   
    def get_neighbors(src_node):
        list_of_neighbors = []
        # loop through all nodes
        for node_1, node_2 in self.all_edges.keys():
            # Check if node_1 is the src_node and the other end node isn't in the list
            if node_1 == src_node and node_2 not in list_of_neighbors:
                # If so, add the end node
                list_of_neighbors.append(node_2)
            if node_2 == src_node and node_1 not in list_of_neighbors:
                list_of_neighbors.append(node_1)
        # Return
        return list_of_neighbors

    def sort_nodes(node, costs):
        return costs[node]

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # Dijkstra's Pseudocode
        # Step 1: Find the cheapest node (latency-wise)
        # Step 2: Update the costs of the neighbors of the ndoe
        # Step 3: Repeat until you've visited every node
        # Step 4: Calc the final path
        # Init Dijkstra's : lowest cost node, parent nodes, etc       
        # Create dicts for cost, and visited nodes
        cost_of_nodes = {}
        parent_nodes = {}
        # Get list of nodes in the network
        list_of_nodes = self.get_nodes()
        # Loop through all nodes
        for node in list_of_nodes:
            # Init cost/parent dicts for each node
            cost_of_nodes[node] = inf
            parent_nodes[node] = -1
        # Set cost of the destination node to 0
        cost_of_nodes[destination] = 0
        # loop through destination nodes neighbors
        for dest_neighbor in self.get_neighbors(destination):
            # Update Cost
            cost_of_nodes[dest_neighbor] = self.all_edges[(dest_neighbor, destination)]
            # Update parent nodes
            parent_nodes[dest_neighbor] = destination
        # Remove Destination
        list_of_nodes.remove(destination)
        # Sort List
        list_of_nodes.sort(key=lambda node: cost_of_nodes[node])
        print(3)

        # Start Dijkstra's 
        while list_of_nodes: 
            min_cost = inf
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
                    new_cost = min_cost + self.all_edges[(min_node, neighbor)]
                    # Check if less than the cost of old path
                    if new_cost < cost_of_nodes[neighbor]:
                        # If so, update cost and path
                        cost_of_nodes[neighbor] = new_cost
                        parent_nodes[neighbor] = min_node


        return parent_nodes[self.id]
