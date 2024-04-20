with matches as (select rowid, distance from nodes_embedding where vss_search (vector_nodes, vss_search_params(json(?), ?))) select rowid, nodes.id, nodes.label, nodes.attributes, matches.distance from matches join nodes on nodes.embed_id = matches.rowid