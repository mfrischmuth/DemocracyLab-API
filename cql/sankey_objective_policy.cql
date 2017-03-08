MATCH
    (o:Objective)-[r_obj:RANKS]-(u:User)-[r_pol:RANKS]-(p:Policy),
    (o)-[:HAS]-(i:Issue)-[:HAS]-(p)
WHERE i.node_id = { issue_id }
RETURN
    o.node_id AS oid,
    o.name AS oname,
    p.node_id AS pid,
    p.name AS pname,
    collect(r_obj.rank) AS oranks,
    collect(r_pol.rank) AS pranks
ORDER BY oid, pid
