import requests

API_KEY = "RGAPI-9b5de20c-59e2-4ef4-8284-8a7d7716b02c"
HEADERS = {"X-Riot-Token": API_KEY}

# 获取王者列表，看第一个entry的字段结构
r = requests.get(
    'https://kr.api.riotgames.com/tft/league/v1/challenger',
    headers=HEADERS, timeout=10
)
data = r.json()
entries = data.get("entries", [])
print(f"Total entries: {len(entries)}")
if entries:
    e = entries[0]
    print(f"Keys: {sorted(e.keys())}")
    print(f"summonerName: {e.get('summonerName')}")
    print(f"summonerId: {e.get('summonerId')}")
    print(f"puuid: {e.get('puuid')}")
    # 看看有没有其他ID字段
    for k in e.keys():
        print(f"  {k}: {str(e[k])[:80]}")
