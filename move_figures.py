import requests, base64, sys

token = sys.argv[1]
repo = "chenyubo123/tft-s17-ml-analysis"
branch = "main"
proxy = {"http": "http://127.0.0.1:9674", "https": "http://127.0.0.1:9674"}
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}

# 1. 获取根目录文件列表
r = requests.get(f"https://api.github.com/repos/{repo}/contents/", 
                 headers=headers, proxies=proxy, timeout=15)
if r.status_code != 200:
    print(f"获取根目录失败: {r.status_code}")
    sys.exit(1)

# 2. 找出所有PNG文件（不在figures/下的）
png_files = [f for f in r.json() if f['name'].endswith('.png') and f['type'] == 'file']
print(f"找到 {len(png_files)} 个散落的PNG文件")

moved = 0
for f in png_files:
    fname = f['name']
    sha = f['sha']
    
    # 3. 获取文件内容
    r2 = requests.get(f["download_url"], headers=headers, proxies=proxy, timeout=15)
    if r2.status_code != 200:
        print(f"  获取 {fname} 内容失败")
        continue
    
    content_b64 = base64.b64encode(r2.content).decode()
    
    # 4. 在figures目录下创建文件
    new_path = f"figures/{fname}"
    data = {"message": f"Move {fname} to figures/", "content": content_b64, "branch": branch}
    r3 = requests.put(f"https://api.github.com/repos/{repo}/contents/{new_path}",
                      headers=headers, json=data, proxies=proxy, timeout=15)
    
    if r3.status_code in (200, 201):
        print(f"  创建: {new_path}")
        
        # 5. 删除根目录下的文件
        del_data = {"message": f"Delete {fname} from root", "sha": sha, "branch": branch}
        r4 = requests.delete(f"https://api.github.com/repos/{repo}/contents/{fname}",
                             headers=headers, json=del_data, proxies=proxy, timeout=15)
        if r4.status_code == 200:
            print(f"  删除: {fname}")
            moved += 1
        else:
            print(f"  删除失败: {fname} ({r4.status_code})")
    else:
        print(f"  创建失败: {new_path} ({r3.status_code}) {r3.text[:100]}")

print(f"\n完成: 移动了 {moved}/{len(png_files)} 个文件")
