## Get All Nodes and Relationships
MATCH (n)-[r]-(m)
RETURN n, r, m
UNION
MATCH (n)
RETURN n, null AS r, null AS m

## Delete EVERYTHING
MATCH (n) DETACH DELETE n

