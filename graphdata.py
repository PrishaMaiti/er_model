import json
import openai

# STEP 1: Natural language input to JSON file
openai.api_key = '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'

# Define the conversation context
conversation = [
    {"role": "system", "content": "You are a user requesting JSON file generation."},
    {"role": "user", "content": ""},
    {"role": "assistant", "content": "Sure! Please provide the details of your database design."},
    # You can include additional conversation turns here if needed
]

# Function to generate the JSON file from natural language input
def create_json_from_prompt(prompt):
    # Update the user's prompt in the conversation
    conversation[1]['content'] = prompt
    
    # Make an API call to ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    
    # Extract the JSON file from the API response
    json_output = None
    for message in response['choices'][0]['message']['content']:
        try:
            json_output = json.loads(message)
            break
        except ValueError:
            continue
    
    return json_output

# STEP 2: Take that JSON file to output a graph data structure that prints out all the different node and edge types

# Build relevant classes for graph
class Node:
    def __init__(self, name, attributes=None):
        self.name = name
        self.attributes = attributes if attributes is not None else []

class Relationship: # aka Edge
    def __init__(self, name, entities, participation=None):
        # participation is a dict of 2 entities e.g. Course, Student, which are entities involved
        # participation qualifies the relationship between 2 nodes/entities
        
        # Sanity check
        if len(entities) != 2:
            print(f'Improper entities param in Relationship CTOR: {entities}')
            return None
        
        self.name = name

        # Sanity check for node names match between entities & participation
        if len(entities) != len(participation.keys()):
            print(f'Non-matching entities & participation params in Relationship CTOR: {participation.keys()}')
            return None
        for i_name in entities:
            if not i_name in participation.keys():
                print(f'entity-name not found in participation keys, in Relationship CTOR: {i_name}')
                return None

        self.entities = entities

        # each key within a participation-entity is a dict of min/max
        self.participation = participation

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_edge(self, relationship):
        self.edges.append(relationship)
    
    def num_nodes(self):
        return len(self.nodes.keys())
    
    def num_edges(self):
        return len(self.edges)
    
    # def get_edges_by_cardinality(self, participation_cardinality_dict):
    #     # example: {"min": 1, "max": 20}
    #     results = []
    #     for rel in self.edges:
    #         for entity in rel.participation.keys():
    #             if entity.get("min") == participation_cardinality_dict.get("min") and entity.get("max") == participation_cardinality_dict.get("max"):
    #                 results.append(rel)
    #     return results
    
    def get_edges_by_name(self, relation_name):
        results = []
        for rel in self.edges:
            if rel.name == relation_name:
                results.append(rel)
                print(f'{rel.name}:', results[0])
        return results


# Create the graph using the JSON input
def create_graph_from_json(json_data):
    graph = Graph()

    # Process entities and attributes
    for entity_data in json_data["entities"]:
        entity_name = entity_data["name"]
        attributes = entity_data.get("attributes", [])
        entity_node = Node(entity_name, attributes)
        graph.add_node(entity_node)

    # Process relationships (edges)
    for relationship_data in json_data["relationships"]:
        relationship_name = relationship_data["name"]
        entities = relationship_data["entities"]
        participation_data = relationship_data.get("participation", {})
        participation = {}

        for entity in entities:
            if entity in participation_data:
                entity_participation = participation_data[entity]
                participation[entity] = entity_participation

        relationship = Relationship(relationship_name, entities, participation)
        graph.add_edge(relationship)

    return graph

# Print the graph output in terminal
def print_graph(graph):
    print("Nodes:")

    # Print entities and attributes
    for node_name, node in graph.nodes.items():
        if isinstance(node, Node):
            print(f"Entity Node: {node_name}")
            print("Attribute Nodes:")
            for attribute in node.attributes:
                if "attributes" in attribute:
                    # Print composite attribute
                    composite_attributes = attribute["attributes"]
                    for composite_attribute in composite_attributes:
                        print(f"    - {composite_attribute}")
                else:
                    # Print single-valued attribute
                    attribute_name = attribute["name"]
                    attribute_type = attribute["type"]
                    print(f"    - {attribute_name}: {attribute_type}")

    # Print relationships (edges)
    print("\nEdges:")
    for relationship in graph.edges:
        print(f"Relationship: {relationship.name}")
        print("Entities:")
        for entity in relationship.entities:
            print(f"    - {entity}")
        print("Participation:")
        for entity, participation in relationship.participation.items():
            print(f"    - {entity}: min={participation['min']}, max={participation['max']}")

    print()

# STEP 3: Convert the graph back to the original JSON that was generated in the first step
def graph_to_json(graph):
    entities = []
    for node_name, node in graph.nodes.items():
        attributes = [{"name": attr["name"], "type": attr["type"]} for attr in node.attributes]
        entity_data = {"name": node_name, "attributes": attributes}
        entities.append(entity_data)

    relationships = []
    for edge in graph.edges:
        participation = edge.participation
        relationship_data = {
            "name": edge.name,
            "entities": edge.entities,
            "participation": participation
        }
        relationships.append(relationship_data)

    json_data = {"entities": entities, "relationships": relationships}
    return json.dumps(json_data, indent=4)




# TESTS
def test1(): # Test graph_to_json function
    # Read JSON data from file
    with open("data.json", "r") as file:
        json_data = json.load(file)

    # Create the graph from the JSON data
    graph = create_graph_from_json(json_data)
    print("Graph: \n")
    print_graph(graph)
    converted_json = graph_to_json(graph)
    print("Converted JSON: \n")
    print(converted_json)

# Invoke the desired test(s)
test1()
