import networkx as nx
import random

# Function to find the shortest path and total weights between two locations
def find_shortest_path_and_weights(graph, current_location, destination):
    try:
        # Calculate the shortest path using Dijkstra's algorithm
        shortest_path = nx.shortest_path(graph, source=current_location, target=destination, weight='weight')
        # Calculate the total weights of the shortest path
        total_weights = nx.shortest_path_length(graph, source=current_location, target=destination, weight='weight')
        return shortest_path, total_weights
    except nx.NetworkXNoPath:
        return None, float('inf')  # Return None if no path exists

# Example usage:
if __name__ == "__main__":
    # List of districts in Tamil Nadu
    districts = ['Madurai', 'Coimbatore', 'Tirupur', 'Erode', 'Chennai', 'KannyaKumari', 'Kumbakonam', 
                 'Palani', 'Thanjavur', 'Puthukotai', 'Pollachi', 'Salem', 'Krishnagiri']
    
    # Create an empty graph
    G = nx.Graph()

    # Add nodes to the graph
    G.add_nodes_from(districts)

    # Define the distances between Coimbatore and Chennai
    dist_coimbatore_chennai = 4

    # Assign random weights to the edges
    for i in range(len(districts)):
        for j in range(i+1, len(districts)):
            if districts[i] == 'Coimbatore' and districts[j] == 'Chennai':
                weight = dist_coimbatore_chennai
            elif districts[i] == 'Chennai' and districts[j] == 'Coimbatore':
                weight = dist_coimbatore_chennai
            else:
                # Assign random weight (distance) between 1 and 100
                weight = random.randint(6, 100)  # Ensure longer distances for other edges
            # Add edge between two nodes with the random weight
            G.add_edge(districts[i], districts[j], weight=weight)
    
    # Current location and destination
    current_location = 'Coimbatore'
    destination = 'Chennai'

    # Find the shortest path and total weights between current location and destination
    shortest_path, total_weights = find_shortest_path_and_weights(G, current_location, destination)

    if shortest_path:
        print(f"Shortest Path from {current_location} to {destination}: {shortest_path}")
        print(f"Total weights: {total_weights}")
    else:
        print(f"No path found from {current_location} to {destination}")
