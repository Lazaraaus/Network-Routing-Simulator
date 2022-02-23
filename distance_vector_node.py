from simulator.node import Node
import copy
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # Class Attributes
        self.route_table = {} # node: {} -> keys: ['latency', 'path'] -> 'latency': latency, 'path': [list of nodes]
        self.link_costs = {} # node:{} -> keys: ['latency', 'neighbor']
        self.neighbors_rout_table = {} # neighbor: {}  -> keys:['latency', 'path'] # Need Seq_nums
        self.seq_num = 0 # Node Seq Num
    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            # Delete Node
            self.neighbors.remove(neighbor)
            self.link_costs.poop(neighbor)
            self.dv.pop(neighbor)
            self.neighbors_rout_table.pop(neighbor)
        else:
            # Check if new neighbor
            if neighbor not in self.neighbors:
                # If so, add neighbor to list
                self.neighbors.append(neighbor)
            # Update Link Cost for neighbor
            self.link_costs.update({neighbor:{}})
            self.link_costs[neighbor]['latency'] = latency
            self.link_costs[neighbor]['neighbor'] = neighbor
        # For all destinations y in N:
        # Deep Copy Current Link Costs? 
        possible_dist_vec = copy.deepcopy(self.link_costs)
        # Loop through all neighbor nodes to get neighbor dist_vec
        for neighbor_node in self.neighbors:
            # Find if we have neighbor rout table
            if neighbor_node in self.neighbors_rout_table.keys():
                # Loop through table for neighbor_node
                for dest_node in self.neighbors_rout_table[neighbor_node]:
                    # Check if dest_node is unknown to self node
                    # Check to make sure self node isn't in neighbors rout table
                    if dest_node not in possible_dist_vec.keys() and self.id not in self.neighbors_rout_table[neighbor_node][dest_node]['path']:
                        # If so,
                        # Update possible_dist_vec
                        possible_dist_vec.update({dest_node:{}})
                        possible_dist_vec[dest_node]['latency'] = 0
                        possible_dist_vec[dest_node]['path'] = []
                        # Get values for update
                        new_cost = self.neighbors_rout_table[neighbor_node][dest_node]['latency'] + self.link_costs[neighbor_node]['latency'] # New Cost
                        possible_dist_vec[dest_node]['latency'] = new_cost
                        new_path = [neighbor_node] + self.neighbors_rout_table[neighbor_node][dest_node]['path'] # New Path
                        possible_dist_vec[dest_node]['path'] = new_path
                
                    # self node and neighbor_node share dest_node
                    elif self.id not in self.neighbors_rout_table[neighbor_node][dest_node]['path']:
                        # Check if cost needs to be updated
                        new_cost = self.neighbors_rout_table[neighbor_node][dest_node]['latency'] + self.link_costs[neighbor_node]['latency']
                        if new_cost < possible_dist_vec[dest_node]['latency']:
                            possible_dist_vec[dest_node]['latency'] = new_cost
                            new_path = [neighbor_node] + self.neighbors_rout_table[neighbor_node][dest_node]['path']
                            possible_dist_vec[dest_node]['path'] = new_path

        # Check if our route table is different 
        if self.route_table != possible_dist_vec:
            # Assign new route table
            self.route_table = possible_dist_vec
            # Construct msg
            broadcast = json.dumps([self.id, self.route_table, self.seq])
            # Incr seq_num
            self.seq_num += 1
            # Send Broadcast to Neighbors
            self.send_to_neighbors(broadcast)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # Unpack incoming message
        in_node, in_node_dv, seq_num = json.loads(m)
        # Check if new to processing node
        if in_node not in self.neighbors_rout_table.keys():
            self.neighbors_rout_table.update({in_node:in_node_dv})

        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
