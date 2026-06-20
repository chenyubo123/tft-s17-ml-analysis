import json

d = json.load(open('data/cf_data.json', 'r', encoding='utf-8'))
keys = list(d['champItems'].keys())

print("=== 所有棋子 ===")
for k in sorted(keys):
    total = d['champTotal'].get(k, 0)
    # 标记非中文命名的
    has_cjk = any('\u4e00' <= c <= '\u9fff' for c in k)
    tag = " *** 非中文名" if not has_cjk else ""
    print(f"  {k} ({total}场){tag}")

print(f"\n总计 {len(keys)} 个棋子")
