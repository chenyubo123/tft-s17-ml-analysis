import requests, os, base64, sys

token = sys.argv[1]
repo = "chenyubo123/tft-s17-ml-analysis"
branch = "main"
proxy = {"http": "http://127.0.0.1:9674", "https": "http://127.0.0.1:9674"}
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}

fig_dir = r"D:\机器学习\TFT项目\figures"
uploaded = 0

# 获取已有文件SHA
existing = {}
r = requests.get(f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1",
                 headers=headers, proxies=proxy, timeout=15)
if r.status_code == 200:
    for item in r.json().get("tree", []):
        existing[item["path"]] = item["sha"]
    print(f"Found {len(existing)} existing files")
else:
    print(f"Tree query failed: {r.status_code} {r.text[:200]}")
    sys.exit(1)

for fname in sorted(os.listdir(fig_dir)):
    if not fname.lower().endswith(".png"):
        continue
    fpath = os.path.join(fig_dir, fname)
    file_path = f"figures/{fname}"
    with open(fpath, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    data = {"message": f"Add figure: {fname}", "content": content_b64, "branch": branch}
    if file_path in existing:
        data["sha"] = existing[file_path]

    r = requests.put(f"https://api.github.com/repos/{repo}/contents/{file_path}",
                     headers=headers, json=data, proxies=proxy, timeout=30)

    if r.status_code in (200, 201):
        print(f"  OK: {fname}")
        uploaded += 1
    else:
        print(f"  FAIL: {fname} ({r.status_code}) {r.text[:100]}")

print(f"\nDone: {uploaded} figures uploaded")
