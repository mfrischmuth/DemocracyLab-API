MATCH
    (v:Value)-[r1:RANKS]-(u:User)-[r2:RANKS]-(o:Objective)
WITH
    v.node_id AS v,
    v.name AS vname,
    o.node_id AS o,
    o.name AS oname,
    r1.rank AS r1,
    r2.rank AS r2,
    // convert likert scale to negative (-1) -> neutral (0) -> positive (1)
    CASE r1.rank
        WHEN -2 THEN -1
        WHEN -1 THEN -1
        WHEN 0 THEN 0
        WHEN 1 THEN 1
        WHEN 2 THEN 1
    END AS r1group,
    CASE r2.rank
        WHEN -2 THEN -1
        WHEN -1 THEN -1
        WHEN 0 THEN 0
        WHEN 1 THEN 1
        WHEN 2 THEN 1
    END AS r2group,
    COUNT(distinct u) AS count
WHERE r1group <> 0 and r2group <> 0
WITH
    vname, oname,
    STR(r1group) + ":" + STR(r2group) AS group,
    SUM(count * (ABS(r1) + ABS(r2))) AS score
ORDER BY score DESC
RETURN vname, oname, group, score
