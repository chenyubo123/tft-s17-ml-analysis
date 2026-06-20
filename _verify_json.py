import json
c = json.load(open("data/cluster_data.json", "r", encoding="utf-8"))
print(f"Clusters: {len(c['clusters'])}")
cf = json.load(open("data/cf_data.json", "r", encoding="utf-8"))
print(f"Champions: {len(cf['champItems'])}, Search keys: {len(cf['searchIndex'])}")
