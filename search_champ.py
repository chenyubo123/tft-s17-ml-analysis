"""
交互式棋子装备搜索工具
输入棋子名称（中文或英文），显示500局真实对局中该棋子最佳装备推荐
样本不足时自动警告
"""
import pandas as pd
import numpy as np
from collections import defaultdict
from collab_filter import (
    load_and_build_matrix, name_champ, name_item,
    parse_item_col, is_valid_item, COMPONENTS, CHAMP_CN, ITEM_CN
)


def build_champion_item_dict(mat_df):
    """构建 {champion_api_name: [dict, ...]} 按综合得分降序"""
    mat_df = mat_df.copy()
    # 综合得分 = 前四率 * log(出场次数) —— 胜率高且样本大
    mat_df["score"] = mat_df["top4_rate"] * np.log1p(mat_df["games"])

    champ_dict = {}
    for champ in mat_df["champion"].unique():
        champ_data = mat_df[mat_df["champion"] == champ].sort_values("score", ascending=False)
        items = []
        for _, row in champ_data.iterrows():
            items.append({
                "item_cn": name_item(row["item"]),
                "item_id": row["item"],
                "top4_rate": row["top4_rate"],
                "games": int(row["games"]),
                "avg_placement": row["avg_placement"],
                "top1_rate": row["top1_rate"],
                "score": row["score"],
            })
        champ_dict[champ] = items
    return champ_dict


def search_champion(query, champ_dict):
    """多级匹配：精确API名 -> 精确中文名 -> 子串匹配API名 -> 子串匹配中文名"""
    cn_to_api = {v: k for k, v in CHAMP_CN.items()}

    # 1. 精确匹配 API 名
    if query in champ_dict:
        return query, champ_dict[query]

    # 2. 精确匹配中文名
    if query in cn_to_api:
        api_name = cn_to_api[query]
        if api_name in champ_dict:
            return api_name, champ_dict[api_name]

    query_lower = query.lower()

    # 3. 子串匹配 API 名
    matches = []
    for api_name in champ_dict:
        if query_lower in api_name.lower():
            matches.append(api_name)
    if len(matches) == 1:
        return matches[0], champ_dict[matches[0]]
    if len(matches) > 1:
        print(f"\n  找到 {len(matches)} 个匹配的棋子（API名）:")
        for m in matches:
            print(f"    {m} ({name_champ(m)})")
        return "__multiple__", None

    # 4. 子串匹配中文名
    cn_matches = []
    for api_name in champ_dict:
        cn = name_champ(api_name)
        if query in cn or query_lower in cn:
            cn_matches.append(api_name)
    if len(cn_matches) == 1:
        return cn_matches[0], champ_dict[cn_matches[0]]
    if len(cn_matches) > 1:
        print(f"\n  找到 {len(cn_matches)} 个匹配的棋子（中文名）:")
        for m in cn_matches:
            print(f"    {name_champ(m)} ({m})")
        return "__multiple__", None

    return None, None


def show_recommendation(champ_name, items, mat_df, min_sample=10):
    """展示棋子装备推荐，样本不足时警告"""
    cn = name_champ(champ_name)
    total_games = sum(item["games"] for item in items)

    print(f"\n{'='*60}")
    print(f"  {cn} ({champ_name})")
    print(f"  数据: 韩服 Challenger/GM/Master  496局真实对局")
    print(f"  该棋子总装备出场次数: {total_games}")
    print(f"{'='*60}")

    if total_games < min_sample:
        print(f"\n  [!!] 样本数量严重不足!")
        print(f"  该棋子仅出场 {total_games} 次，统计意义很低。")
        print(f"  阈值: >= {min_sample} 局才具参考价值。\n")

    # 过滤掉出场 < 5 局的装备
    valid_items = [it for it in items if it["games"] >= 5]

    if not valid_items:
        print(f"\n  该棋子无足够装备数据（每件装备至少需5局出场）。")
        return

    top_items = valid_items[:8]

    print(f"\n  {'排名':<4} {'装备':<22} {'前四率':<8} {'均排':<6} {'出场':<6} {'评分':<8} {'评价'}")
    print(f"  {'-'*70}")

    for rank, it in enumerate(top_items, 1):
        wr = it["top4_rate"]
        if wr >= 0.60:
            tag = "[强力推荐]"
        elif wr >= 0.52:
            tag = "[可用]"
        elif wr >= 0.48:
            tag = "[一般]"
        else:
            tag = "[不推荐]"

        print(f"  {rank:<4} {it['item_cn']:<22} {wr:.1%}     {it['avg_placement']:.2f}   "
              f"{it['games']:<6} {it['score']:.3f}   {tag}")

    # BIS 三件套
    bis = top_items[:3]
    print(f"\n  >>> 推荐三件套 (BIS) <<<")
    for i, it in enumerate(bis, 1):
        print(f"  {i}. {it['item_cn']:<22} (前四率={it['top4_rate']:.1%}, 出场={it['games']}局, "
              f"均排={it['avg_placement']:.2f})")

    if total_games < min_sample:
        print(f"\n  [!!] 再次提醒: 总样本={total_games}局 < {min_sample}局阈值，结果仅供参考!")


def list_champions(champ_dict):
    """列出所有可用棋子"""
    champs_list = sorted(champ_dict.keys())
    print(f"\n  可用棋子 ({len(champs_list)} 个):")
    for i, c in enumerate(champs_list):
        cn = name_champ(c)
        total = sum(it["games"] for it in champ_dict[c])
        warn = " [样本少!]" if total < 10 else ""
        print(f"    {cn:<12} ({c:<20}) {total:>4}局{warn}", end="")
        if (i + 1) % 3 == 0:
            print()
    if len(champs_list) % 3 != 0:
        print()


def main():
    print("\n" + "=" * 60)
    print("  TFT S17 交互式棋子装备搜索")
    print("  数据来源: Riot API 韩服 Challenger/GM/Master")
    print("  输入棋子中文名或英文名查看装备推荐")
    print("  输入 list / l  查看所有棋子")
    print("  输入 q / quit  退出")
    print("=" * 60)

    print("\n[加载] 正在解析496局对局数据...")
    mat_df, _ = load_and_build_matrix()
    champ_dict = build_champion_item_dict(mat_df)
    print(f"[完成] 共 {len(champ_dict)} 个棋子, {len(mat_df)} 条棋子-装备组合")

    while True:
        try:
            query = input("\n请输入棋子名称 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出。")
            break

        if not query:
            continue

        if query.lower() in ("q", "quit", "exit", "退出"):
            print("再见!")
            break

        if query.lower() in ("list", "l", "列表"):
            list_champions(champ_dict)
            continue

        champ_name, items = search_champion(query, champ_dict)

        if champ_name is None:
            print(f"\n  未找到棋子 '{query}'")
            print("  提示: 输入 list 查看所有可用棋子")
            continue

        if champ_name == "__multiple__":
            print("  请输入更精确的名称（支持中英文子串匹配）")
            continue

        show_recommendation(champ_name, items, mat_df, min_sample=10)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # 命令行直接查询模式: python search_champ.py 亚托克斯
        query = " ".join(sys.argv[1:])
        print(f"\n[查询] {query}")
        mat_df, _ = load_and_build_matrix()
        champ_dict = build_champion_item_dict(mat_df)
        champ_name, items = search_champion(query, champ_dict)
        if champ_name is None:
            print(f"未找到棋子 '{query}'")
        elif champ_name == "__multiple__":
            print("请输入更精确的名称")
        else:
            show_recommendation(champ_name, items, mat_df, min_sample=10)
    else:
        main()
