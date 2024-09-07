from falkordb import FalkorDB
import json

# Initialize the FalkorDB client
db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('MyGraph')

def run_query(graph, query):
    result = graph.query(query)
    print(f"Query: {query}")
    print(f"Headers: {result.header}")
    print(f"Data: {result.result_set}")
    return result.result_set

def get_detailed_schema():
    # Get all labels (node types)
    labels_query = "CALL db.labels() YIELD label"
    labels = run_query(graph, labels_query)
    labels = [label[0] for label in labels]  # Assuming each label is in the first column

    schema = {}

    for label in labels:
        label_info = {"properties": [], "relationships": []}

        # Get properties for this label
        properties_query = f"""
        MATCH (n:{label})
        UNWIND keys(n) AS prop
        RETURN DISTINCT prop
        """
        properties = run_query(graph, properties_query)
        label_info["properties"] = [prop[0] for prop in properties]  # Assuming each property is in the first column

        # Get outgoing relationships for this label
        outgoing_relationships_query = f"""
        MATCH (n:{label})-[r]->(m)
        RETURN DISTINCT type(r) AS relationship_type, labels(m) AS target_labels
        """
        outgoing_relationships = run_query(graph, outgoing_relationships_query)
        
        for rel in outgoing_relationships:
            label_info["relationships"].append({
                "type": rel[0],  # Assuming relationship_type is in the first column
                "direction": "outgoing",
                "target_labels": rel[1]  # Assuming target_labels is in the second column
            })

        # Get incoming relationships for this label
        incoming_relationships_query = f"""
        MATCH (n:{label})<-[r]-(m)
        RETURN DISTINCT type(r) AS relationship_type, labels(m) AS source_labels
        """
        incoming_relationships = run_query(graph, incoming_relationships_query)
        
        for rel in incoming_relationships:
            label_info["relationships"].append({
                "type": rel[0],  # Assuming relationship_type is in the first column
                "direction": "incoming",
                "source_labels": rel[1]  # Assuming source_labels is in the second column
            })

        schema[label] = label_info

    return json.dumps(schema, indent=4)

# Print the detailed schema JSON
print(get_detailed_schema())