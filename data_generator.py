"""
TFT 对局数据生成器
模拟云顶之弈对局数据，包含棋子、羁绊、装备及最终排名
"""

import numpy as np
import pandas as pd
from config import CHAMPIONS, TRAITS, ITEMS, META_COMPS

np.random.seed(20231060)


def generate_matches(n_matches=500):
    """
    生成 n_matches 局 TFT 对局数据。
    每局8名玩家，部分遵循已知Meta阵容（Top4率高），部分随机（后四率高）。
    
    返回 DataFrame，每行代表一名玩家的最终阵容。
    """
    all_players = []
    champion_keys = list(CHAMPIONS.keys())
    trait_keys = list(TRAITS.keys())
    item_keys = list(ITEMS.keys())

    for match_id in range(1, n_matches + 1):
        # 随机选 4~6 个"Meta玩家"（遵循已知强势阵容）
        n_meta = np.random.randint(4, 7)
        meta_indices = np.random.choice(len(META_COMPS), size=n_meta, replace=True)

        players_in_match = []

        for slot in range(8):
            if slot < n_meta:
                comp = META_COMPS[meta_indices[slot]]
                board = _build_meta_board(comp, champion_keys, trait_keys, item_keys)
                board["match_id"] = match_id
                # Meta阵容的排名在1~5之间（高概率前四）
                base_placement = np.random.randint(1, 5)
            else:
                comp = None
                board = _build_random_board(champion_keys, trait_keys, item_keys)
                board["match_id"] = match_id
                # 随机阵容的排名在3~8之间（高概率后四）
                base_placement = np.random.randint(3, 9)

            board["placement"] = base_placement
            board["win"] = 1 if base_placement <= 4 else 0
            players_in_match.append(board)

        # 确保8人不重名次
        placements = sorted(range(8), key=lambda x: players_in_match[x]["placement"] + np.random.uniform(-0.3, 0.3))
        for rank, idx in enumerate(placements):
            players_in_match[idx]["placement"] = rank + 1
            players_in_match[idx]["win"] = 1 if rank < 4 else 0

        all_players.extend(players_in_match)

    return pd.DataFrame(all_players)


def _build_meta_board(comp, champion_keys, trait_keys, item_keys):
    """根据已知Meta阵容模板构建玩家棋盘"""
    board = {"level": np.random.randint(7, 10), "gold_left": np.random.randint(10, 80)}

    # --- 羁绊特征 ---
    for t in trait_keys:
        board[f"syn_{t}"] = 0
    # 激活核心羁绊（包含等级：1, 2, 3等）
    for trait_name, tier in comp["traits"].items():
        if trait_name in trait_keys:
            board[f"syn_{trait_name}"] = tier

    # --- 棋子（9人口，但 unit_ 只标记核心棋子 > 0） ---
    for c in champion_keys:
        board[f"unit_{c}"] = 0
    for u in comp["core_units"]:
        if u in champion_keys:
            board[f"unit_{u}"] = np.random.choice([1, 2], p=[0.6, 0.4])  # 1=二星, 2=三星

    # 额外随机填充几个棋子模拟完整9人口
    extra_units = [u for u in champion_keys if u not in comp["core_units"]]
    extra_picks = np.random.choice(extra_units, size=min(4, len(extra_units)), replace=False)
    for u in extra_picks:
        board[f"unit_{u}"] = np.random.choice([1, 2], p=[0.7, 0.3])

    # --- 装备 ---
    for champ_api, item_list in comp["core_items"].items():
        for item in item_list:
            col = f"{champ_api}_with_{item}"
            board[col] = 0
    # 所有可能的 champ×item 组合
    for c in champion_keys:
        for it in item_keys:
            col = f"{c}_with_{it}"
            if col not in board:
                board[col] = 0

    for champ_api, item_list in comp["core_items"].items():
        for item in item_list:
            col = f"{champ_api}_with_{item}"
            board[col] = 1

    # 额外随机装备（少量噪声）
    noise_count = np.random.randint(2, 6)
    for _ in range(noise_count):
        c = np.random.choice(champion_keys)
        it = np.random.choice(item_keys)
        board[f"{c}_with_{it}"] = 1

    return board


def _build_random_board(champion_keys, trait_keys, item_keys):
    """构建随机阵容（用于产生"非Meta"后四玩家）"""
    board = {"level": np.random.randint(6, 10), "gold_left": np.random.randint(0, 60)}

    # --- 羁绊：随机激活若干羁绊，等级1~3 ---
    for t in trait_keys:
        board[f"syn_{t}"] = 0
    n_traits = np.random.randint(1, 6)
    active_traits = np.random.choice(trait_keys, size=n_traits, replace=False)
    for t in active_traits:
        board[f"syn_{t}"] = np.random.randint(1, 4)

    # --- 棋子：随机选8~10个 ---
    for c in champion_keys:
        board[f"unit_{c}"] = 0
    n_units = np.random.randint(8, 11)
    active_units = np.random.choice(champion_keys, size=n_units, replace=False)
    for u in active_units:
        board[f"unit_{u}"] = np.random.choice([1, 2], p=[0.8, 0.2])

    # --- 装备：随机 ---
    for c in champion_keys:
        for it in item_keys:
            board[f"{c}_with_{it}"] = 0
    n_items = np.random.randint(6, 15)
    for _ in range(n_items):
        c = np.random.choice(active_units)
        it = np.random.choice(item_keys)
        board[f"{c}_with_{it}"] = 1

    return board


def add_macro_features(df):
    """添加宏观经济指标列（阵容相对价值、相对等级）"""
    df["ratio_level"] = df["level"] / df.groupby("match_id")["level"].transform("mean")
    df["ratio_gold"] = df["gold_left"] / (df.groupby("match_id")["gold_left"].transform("mean") + 1)
    return df


def clean_data(df):
    """数据清洗：去除异常局（如末尾玩家金币极少=愤怒卖卡）"""
    before = len(df)
    df = df[~(df["win"] == 0) | (df["gold_left"] >= 10)]
    print(f"数据清洗: {before} -> {len(df)} 行 (去除愤怒卖卡局)")
    return df


if __name__ == "__main__":
    df = generate_matches(500)
    df = add_macro_features(df)
    df = clean_data(df)
    df.to_parquet("data/tft_dump.parquet", index=False)
    print(f"\n数据集已生成: data/tft_dump.parquet ({len(df)} 行)")
    print(f"Meta对局数: ~{(df['win'].mean()*100):.1f}% 前四率")
