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
            msg = json.dumps([self.id, neighbor, latency, self.get_time()])
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
                broadcast = json.dumps([self.id, neighbor, latency, self.get_time()])
                self.send_to_neighbors(broadcast)
                # Loop and share link with individual nodes in Neighbors
                for node_1, node_2 in self.all_edges.keys():
                    link_latency = self.all_edges[(node_1, node_2)]
                    link_sq_num = self.edges_sq_num[(node_1, node_2)]
                    broadcast = json.dumps([node_1, node_2, link_latency, link_sq_num])
                    self.send_to_neighbor(neighbor, broadcast)

            # Neighbor already in Neighbors
            else:
                # Check if latency was updated on link
                if prev_cost != latency:
                    # Update seq_nums 
                    self.edges_sq_num[(self.id, neighbor)] = self.get_time()
                    self.edges_sq_num[(neighbor, self.id)] = self.get_time()
                    # Construct Msg
                    broadcast = json.dumps([self.id, neighbor, latency, self.get_time()])
                    # Send Msg
                    self.send_to_neighbors(broadcast)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        # Deconstruct Msg
        node_1, node_2, latency, seq_num = json.loads(m)
        # CASE 1: THERE IS NO SEQ_NUM n1 or n2 
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
            broadcast = json.dumps([node_1, node_2, latency, seq_num])

        else:
            # Check old_seq_num against seq_num
            if seq_num > old_seq_num:
                # Update latency, seq_num, broadcast
                self.edges_seq[()]
                pass

        # CASE 2: THERE IS: Compare to see which node has older info
        # CASE 3: THIS NODE HAS RECENT INFO - Back Propagate to Sender Node
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
