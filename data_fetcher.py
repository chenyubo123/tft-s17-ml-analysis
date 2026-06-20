"""
Riot API 数据拉取 —— 从官方服务器获取 S17 真实对局数据
生成格式兼容 main.py 的 parquet 文件
"""

import requests
import time
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

API_KEY = "RGAPI-9b5de20c-59e2-4ef4-8284-8a7d7716b02c"

# 韩国服务器 (最大玩家基数，Meta数据最丰富)
PLATFORM = "kr"      # kr.api.riotgames.com
REGION = "asia"      # asia.api.riotgames.com (match routing)
PLATFORM_HOST = f"https://{PLATFORM}.api.riotgames.com"
REGION_HOST = f"https://{REGION}.api.riotgames.com"

HEADERS = {"X-Riot-Token": API_KEY}
CALL_INTERVAL = 1.2   # 每1.2秒一次调用 ≈ 50次/分钟，安全低于100上限
MAX_MATCHES = 500      # 目标对局数
MAX_PLAYERS = 100       # 初始拉取的高分玩家数

# 请求计数器（监控速率限制）
request_count = 0


def api_get(url, desc=""):
    """限速 API 调用"""
    global request_count
    time.sleep(CALL_INTERVAL)
    request_count += 1
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            print(f"  [限速] 等待 {retry_after}s...")
            time.sleep(retry_after + 2)
            resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [API错误] {desc}: {e}")
        return None


def step1_get_high_elo_puuids():
    """拉取王者/宗师/大师玩家的 PUUID（新版API直接返回puuid）"""
    print("\n[Step 1] 拉取高分段玩家列表...")

    puuids = []  # [(puuid, tier, rank), ...]

    leagues = [
        ("challenger", "CHALLENGER"),
        ("grandmaster", "GRANDMASTER"),
        ("master", "MASTER"),
    ]

    for endpoint, tier_label in leagues:
        if len(puuids) >= MAX_PLAYERS:
            break

        data = api_get(f"{PLATFORM_HOST}/tft/league/v1/{endpoint}", f"获取{tier_label}列表")
        if not data:
            continue

        entries = data.get("entries", [])
        print(f"  [{tier_label}] 获取到 {len(entries)} 个玩家")
        for entry in entries:
            puuid = entry.get("puuid")
            rank = entry.get("rank", "I")
            if puuid:
                puuids.append((puuid, tier_label, rank))
            if len(puuids) >= MAX_PLAYERS:
                break

    print(f"  → 获取到 {len(puuids)} 个高分玩家PUUID")
    return puuids


def step2_fetch_match_ids(puuids):
    """从每个玩家的历史记录获取 S17 对局ID"""
    print("\n[Step 2] 拉取玩家对局记录...")

    match_ids = set()  # 去重

    for puuid, tier, rank in puuids:
        if len(match_ids) >= MAX_MATCHES * 2:  # 多拿一些，后面要筛选
            break

        data = api_get(
            f"{REGION_HOST}/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=20",
            f"获取{tier}玩家对局"
        )
        if data:
            match_ids.update(data)

    print(f"  → 获取到 {len(match_ids)} 个对局ID（去重后）")
    return list(match_ids)


def step3_fetch_match_details(match_ids):
    """拉取对局详情，只保留 S17 (Version 17.x) 的对局"""
    print(f"\n[Step 3] 拉取对局详细数据（目标: {MAX_MATCHES} 局 S17）...")

    all_matches = []
    discarded = 0
    s17_count = 0

    for i, match_id in enumerate(match_ids):
        if s17_count >= MAX_MATCHES:
            break

        if (i + 1) % 50 == 0:
            print(f"  进度: {i+1}/{len(match_ids)} (有效S17: {s17_count}, 丢弃: {discarded})")

        data = api_get(
            f"{REGION_HOST}/tft/match/v1/matches/{match_id}",
            f"获取对局 {match_id}"
        )
        if not data:
            continue

        # 只保留 S17 (tft_set_number == 17)
        set_number = data.get("info", {}).get("tft_set_number", 0)
        if set_number != 17:
            discarded += 1
            continue

        all_matches.append(data)
        s17_count += 1

    print(f"  → 拉取完成: S17对局 {s17_count} 局, 丢弃其他版本 {discarded} 局")
    print(f"  → 累计API调用: {request_count}")
    return all_matches


def step4_parse_to_dataframe(matches):
    """将对局详情解析为 pandas DataFrame（兼容 main.py 格式）"""
    print(f"\n[Step 4] 解析对局数据...")

    # 动态收集所有出现的棋子、羁绊、装备
    all_champions = set()
    all_traits = set()
    all_items = set()

    rows = []

    for match in matches:
        info = match.get("info", {})
        participants = info.get("participants", [])

        for p in participants:
            placement = p.get("placement", 8)
            level = p.get("level", 1)
            gold_left = p.get("gold_left", 0)

            row = {
                "match_id": match["metadata"]["match_id"],
                "placement": placement,
                "win": 1 if placement <= 4 else 0,
                "level": level,
                "gold_left": gold_left,
            }

            # --- 棋子 (unit_xxx = 星级) ---
            units_data = {}
            for unit in p.get("units", []):
                char_id = unit.get("character_id", "")
                tier = unit.get("tier", 1)  # 1=一星, 2=二星, 3=三星
                all_champions.add(char_id)
                units_data[char_id] = tier

                # 装备 (item_ItemId_ChampionId)
                for item_name in unit.get("itemNames", []):
                    all_items.add(item_name)
                    row[f"item_{item_name}_{char_id}"] = 1

            # --- 羁绊 (syn_TraitName = 等级) ---
            traits_data = {}
            for trait in p.get("traits", []):
                trait_name = trait.get("name", "")
                tier = trait.get("tier_current", 0)
                all_traits.add(trait_name)
                traits_data[trait_name] = tier

            # 先收集到临时列表，最后统一构建 DataFrame
            row["_units"] = units_data
            row["_traits"] = traits_data
            rows.append(row)

    # 统一构建 DataFrame
    df = pd.DataFrame(rows)

    # 展开棋子列
    for champ in sorted(all_champions):
        df[f"unit_{champ}"] = df["_units"].apply(lambda d, c=champ: d.get(c, 0))

    # 展开羁绊列
    for trait in sorted(all_traits):
        df[f"syn_{trait}"] = df["_traits"].apply(lambda d, t=trait: d.get(t, 0))

    # 删除临时列
    df.drop(columns=["_units", "_traits"], inplace=True)

    # 填充缺失的装备列为0
    for col in df.columns:
        if col.startswith("item_") and df[col].dtype == object:
            df[col] = df[col].fillna(0).astype(int)

    print(f"  → 解析完成: {len(df)} 条记录, {df['match_id'].nunique()} 局")
    print(f"  → 棋子种类: {len(all_champions)}, 羁绊种类: {len(all_traits)}, 装备种类: {len(all_items)}")
    print(f"  → 前四率: {df['win'].mean()*100:.1f}% (全量应为50%)")

    # 构建棋子/羁绊名称映射（用于显示）
    champion_names = {}
    trait_names = {}

    for match in matches[:1]:  # 只用第一局建立名称表
        for p in match["info"]["participants"]:
            for unit in p["units"]:
                champion_names[unit["character_id"]] = unit.get(
                    "character_id", ""
                ).replace("TFT17_", "")
            for trait in p["traits"]:
                trait_names[trait["name"]] = trait.get("name", "").replace(
                    "TFT17_", ""
                )

    return df, champion_names, trait_names


def step5_add_filter(df):
    """添加辅助列和过滤"""
    print(f"\n[Step 5] 数据过滤 & 辅助特征...")

    # 统计每局棋子数
    unit_cols = [c for c in df.columns if c.startswith("unit_")]
    df["unit_count"] = (df[unit_cols] > 0).sum(axis=1)

    # 只保留满7人口以上的对局（排除投降/挂机局）
    df = df[df["unit_count"] >= 5].copy()

    # 统计羁绊激活数
    syn_cols = [c for c in df.columns if c.startswith("syn_")]
    df["syn_count"] = (df[syn_cols] > 0).sum(axis=1)

    print(f"  → 过滤后: {len(df)} 条有效记录")
    print(f"  → 每局平均棋子数: {df['unit_count'].mean():.1f}")
    print(f"  → 每局平均羁绊数: {df['syn_count'].mean():.1f}")

    return df


def fetch_and_save():
    """主流程"""
    print("=" * 60)
    print("  Riot API 数据拉取 —— S17 星神赛季")
    print(f"  服务器: {PLATFORM.upper()} ({REGION.upper()} routing)")
    print(f"  目标: {MAX_MATCHES} 局真实对局")
    print("=" * 60)

    # Step 1-3: 获取数据
    puuids = step1_get_high_elo_puuids()
    match_ids = step2_fetch_match_ids(puuids)
    matches = step3_fetch_match_details(match_ids)

    if len(matches) == 0:
        print("\n[失败] 没有获取到任何S17对局数据，请检查:")
        print("  1. API Key 是否有效")
        print("  2. 当前版本是否为 S17 (Version 17.x)")
        print("  3. 区域是否选择了有数据的服务器")
        return

    # Step 4-5: 解析和过滤
    df, champion_names, trait_names = step4_parse_to_dataframe(matches)
    df = step5_add_filter(df)

    # 保存
    Path("data").mkdir(exist_ok=True)
    df.to_parquet("data/tft_dump.parquet", index=False)
    print(f"\n[完成] 数据已保存至 data/tft_dump.parquet")
    print(f"  总记录: {len(df)}, 总对局: {df['match_id'].nunique()}")

    # 保存名称映射
    import json
    with open("data/s17_names.json", "w", encoding="utf-8") as f:
        json.dump({
            "champions": champion_names,
            "traits": trait_names,
        }, f, ensure_ascii=False, indent=2)
    print(f"  名称映射已保存至 data/s17_names.json")

    # 打印前10个棋子/羁绊名称（供核实）
    print(f"\n  棋子样本: {list(champion_names.values())[:15]}")
    print(f"  羁绊样本: {list(trait_names.values())[:15]}")


if __name__ == "__main__":
    fetch_and_save()
