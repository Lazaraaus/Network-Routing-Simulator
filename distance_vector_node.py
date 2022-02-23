from simulator.node import Node
import copy
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # Class Attributes
        self.rout_table = {}
        self.link_costs = {}
        self.neighbors_rout_table = {}
        self.seq_num
    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            # Delete Node
            pass
        else:
            # Check if new neighbor
            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)
            # Update Link Cost
        pass
    # For all destinations y in N:
    # Deep Copy Current Link Cost? 

    # Loop through all neighbor nodes to get neighbor dist_vec
    for neighbor_node in self.neighbors:
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
