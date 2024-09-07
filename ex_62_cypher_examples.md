## Get All Nodes and Relationships
MATCH (n)-[r]-(m)
RETURN n, r, m
UNION
MATCH (n)
RETURN n, null AS r, null AS m

## Delete EVERYTHING
MATCH (n) DETACH DELETE n

## GET VERSION
MATCH (v:Version {name: "plugin.test.spinningcube"}) RETURN v ORDER BY v.updated_utc DESC LIMIT 1

## GET LATEST VERSION AND RELATED ENTITIES
// Find the latest version by name and updated_utc
MATCH (v:Version {name: "plugin.test.spinningcube"})
WITH v
ORDER BY v.updated_utc DESC 
LIMIT 1

// Fetch all related elements to this specific version
MATCH (v)-[r]->(m)
RETURN v,r,m