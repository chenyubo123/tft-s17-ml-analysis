"""
导出网页所需数据: 聚类统计 + CF 推荐 + 棋子搜索索引 -> JSON
"""
import pandas as pd
import numpy as np
import json
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import os

FIG_DIR = "figures"

# ---- 棋子中英文映射 (S17星神赛季完整列表，与collab_filter.py一致) ----
CHAMP_CN = {
    "Aatrox": "亚托克斯", "Akali": "阿卡丽", "AurelionSol": "奥瑞利安·索尔",
    "Aurora": "奥罗拉", "Bard": "巴德", "Belveth": "卑尔维斯",
    "Blitzcrank": "布里茨", "Briar": "贝蕾亚", "Caitlyn": "凯特琳",
    "Chogath": "科加斯", "Corki": "库奇", "Diana": "黛安娜",
    "Ezreal": "伊泽瑞尔", "Fiora": "菲奥娜", "Fizz": "菲兹",
    "Galio": "加里奥", "Gnar": "纳尔", "Gragas": "古拉加斯",
    "Graves": "格雷福斯", "Gwen": "格温", "Illaoi": "俄洛伊",
    "Jax": "贾克斯", "Jhin": "烬", "Jinx": "金克丝",
    "Kaisa": "卡莎", "IvernMinion": "小木灵", "Karma": "卡尔玛", "Kindred": "千珏",
    "Leblanc": "乐芙兰", "Leona": "蕾欧娜", "Lissandra": "丽桑卓",
    "Lulu": "璐璐", "Maokai": "茂凯", "MasterYi": "易大师",
    "Milio": "米利欧", "MissFortune": "厄运小姐", "Mordekaiser": "莫德凯撒",
    "Morgana": "莫甘娜", "Nami": "娜美", "Nasus": "内瑟斯",
    "Nunu": "努努", "Ornn": "奥恩", "Pantheon": "潘森",
    "Poppy": "波比", "Pyke": "派克", "Rammus": "拉莫斯",
    "RekSai": "雷克塞", "Rhaast": "拉亚斯特", "Riven": "锐雯",
    "Samira": "莎弥拉", "Shen": "慎", "Sona": "娑娜",
    "TahmKench": "塔姆·肯奇", "Talon": "泰隆", "Teemo": "提莫",
    "TwistedFate": "崔斯特", "Urgot": "厄加特", "Veigar": "维迦",
    "Vex": "薇古丝", "Viktor": "维克托", "Xayah": "霞",
    "Zed": "劫", "Zoe": "佐伊",
}

# ---- 装备中文名 (S17星神赛季 37件可合成装备) ----
ITEM_CN = {
    "AdaptiveHelm": "适应性头盔", "ArchangelsStaff": "大天使之杖",
    "Bloodthirster": "饮血剑", "BlueBuff": "蓝霸符",
    "BrambleVest": "棘刺背心", "Crownguard": "冕卫",
    "Deathblade": "死亡之刃", "DragonsClaw": "巨龙之爪",
    "EdgeOfNight": "夜之锋刃", "Evenshroud": "薄暮法袍",
    "GargoyleStoneplate": "石像鬼石板甲", "GiantSlayer": "巨人杀手",
    "GuinsoosRageblade": "鬼索的狂暴之刃", "HandOfJustice": "正义之手",
    "HextechGunblade": "海克斯科技枪刃", "InfinityEdge": "无尽之刃",
    "IonicSpark": "离子火花", "JeweledGauntlet": "珠光护手",
    "KrakensFury": "海妖之怒", "LastWhisper": "最后的轻语",
    "Morellonomicon": "莫雷洛秘典", "NashorsTooth": "纳什之牙",
    "ProtectorsVow": "圣盾使的誓约", "Quicksilver": "水银",
    "RabadonsDeathcap": "灭世者的死亡之帽", "RedBuff": "红霸符",
    "SpearOfShojin": "朔极之矛", "SpiritVisage": "振奋盔甲",
    "SteadfastHeart": "坚定之心", "SteraksGage": "斯特拉克的挑战护手",
    "StrikersFlail": "强袭者的链枷", "SunfireCape": "日炎斗篷",
    "ThiefsGloves": "窃贼手套", "TitansResolve": "泰坦的坚决",
    "VoidStaff": "虚空之杖", "WarmogsArmor": "狂徒铠甲",
    "Anomaly": "异常突变",
    # 奥恩神器
    "OrnnDeathsDefiance": "死亡之蔑", "OrnnHorizonFocus": "视界专注",
    "OrnnHullbreaker": "破舰者", "OrnnInfinityForce": "无限之力",
    "OrnnTheCollector": "收集者", "OrnnZhonyasParadox": "中娅悖论",
    # 神器
    "Artifact_AegisOfDawn": "黎明之盾", "Artifact_AegisOfDusk": "黄昏之盾",
    "Artifact_BlightingJewel": "枯萎珠宝", "Artifact_CappaJuice": "卡帕果汁",
    "Artifact_Dawncore": "黎明核心", "Artifact_EternalPact": "永恒契约",
    "Artifact_Fishbones": "鱼骨头", "Artifact_HellfireHatchet": "地狱火斧",
    "Artifact_LichBane": "巫妖之祸", "Artifact_LightshieldCrest": "光盾徽章",
    "Artifact_LudensTempest": "卢登风暴", "Artifact_Mittens": "连指手套",
    "Artifact_NavoriFlickerblades": "纳沃利烁刃",
    "Artifact_ProwlersClaw": "暗行者之爪", "Artifact_RapidFirecannon": "疾射火炮",
    "Artifact_SeekersArmguard": "探索者的护臂",
    "Artifact_SilvermereDawn": "银黎黎明",
    "Artifact_StatikkShiv": "斯塔缇克电刃",
    "Artifact_TalismanOfAscension": "飞升护符",
    "Artifact_TheIndomitable": "不屈之志",
    "Artifact_TitanicHydra": "巨型九头蛇", "Artifact_VoidGauntlet": "虚空护手",
    "Artifact_WitsEnd": "智慧末刃",
    # 特殊装备
    "ForceOfNature": "自然之力", "CrownOfDemacia": "德玛西亚王冠",
    "LavenderCrown": "薰衣草王冠", "ShimmerscaleCrownOfChampions": "冠军王冠",
    "ShimmerscaleDravensAxe": "德莱文之斧",
    "ShimmerscaleGamblersBlade": "赌徒之刃",
    "ShimmerscaleGoldmancersStaff": "金魔法杖",
    "ShimmerscaleMogulsMail": "大亨之铠",
    "SevikasJinxedArm": "塞薇卡的诅咒臂铠",
}

# ---- 颜色映射 ----
def equip_color(ename):
    """根据装备类型返回颜色标签 (S17星神赛季装备)"""
    offensive = [
        "Deathblade", "InfinityEdge", "GiantSlayer", "LastWhisper",
        "GuinsoosRageblade", "SpearOfShojin", "BlueBuff", "ArchangelsStaff",
        "JeweledGauntlet", "RabadonsDeathcap", "Morellonomicon",
        "IonicSpark", "HextechGunblade", "RedBuff", "AdaptiveHelm",
        "KrakensFury", "NashorsTooth", "VoidStaff", "EdgeOfNight",
        "StrikersFlail",
    ]
    defensive = [
        "BrambleVest", "DragonsClaw", "WarmogsArmor", "GargoyleStoneplate",
        "SunfireCape", "TitansResolve", "Crownguard", "SteraksGage",
        "ProtectorsVow", "SpiritVisage", "SteadfastHeart", "Evenshroud",
    ]
    if ename in offensive:
        return "#e74c3c"  # 红色=攻击
    elif ename.startswith("Artifact_") or ename.startswith("Ornn"):
        return "#f39c12"  # 橙色=神器/奥恩
    elif ename.startswith("Shimmerscale") or ename.startswith("Sevika"):
        return "#17C25E"  # 绿色=特殊
    elif ename in defensive:
        return "#3498db"  # 蓝色=防御
    else:
        return "#8e44ad"  # 紫色=其他


def strip_unit_name(col):
    return col.replace("unit_TFT17_", "")

def strip_trait_name(col):
    return col.replace("syn_TFT17_", "")

def main():
    # ---- 加载数据 ----
    df = pd.read_parquet("data/tft_dump.parquet")
    print(f"Data: {len(df)} records, {df['match_id'].nunique()} matches")

    unit_cols_all = [c for c in df.columns if c.startswith("unit_TFT17_")]
    exclude_words = ["PVE", "Enemy", "Summon", "Minion"]
    unit_cols = [c for c in unit_cols_all if not any(ex in c for ex in exclude_words)]
    trait_cols = [c for c in df.columns if c.startswith("syn_TFT17_")]

    # ---- 过滤 ----
    df_filtered = df[df[unit_cols].sum(axis=1) > 0].copy()
    print(f"Filtered: {len(df_filtered)} records")

    # ---- 任务5: 聚类统计 ----
    print("Computing clustering stats...")
    X = df_filtered[trait_cols].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=10, random_state=42, n_init="auto")
    df_filtered["cluster"] = kmeans.fit_predict(X_scaled)

    clusters = []
    for cid in sorted(df_filtered["cluster"].unique()):
        sub = df_filtered[df_filtered["cluster"] == cid]
        n = len(sub)
        wr = sub["win"].mean() * 100
        avg = sub["placement"].mean()

        syn_mean = sub[trait_cols].mean().sort_values(ascending=False).head(6)
        top_traits = []
        for tc, val in syn_mean.items():
            pct = (sub[tc] > 0).mean() * 100
            top_traits.append({
                "name": strip_trait_name(tc),
                "avg": round(float(val), 1),
                "pct": round(float(pct), 0),
            })

        unit_mean = sub[unit_cols].mean().sort_values(ascending=False).head(5)
        top_units = []
        for uc, val in unit_mean.items():
            uname = strip_unit_name(uc)
            top_units.append({
                "name": uname,
                "cn": CHAMP_CN.get(uname, uname),
                "avgStars": round(float(val), 1),
                "pct": round(float((sub[uc] > 0).mean() * 100), 0),
            })

        clusters.append({
            "id": int(cid),
            "n": n,
            "top4": round(float(wr), 1),
            "avgPlace": round(float(avg), 2),
            "traits": top_traits,
            "units": top_units,
        })

    cluster_json = {
        "nClusters": 10,
        "nMatches": int(df_filtered["match_id"].nunique()),
        "nRecords": len(df_filtered),
        "clusters": clusters,
    }

    with open("data/cluster_data.json", "w", encoding="utf-8") as f:
        json.dump(cluster_json, f, ensure_ascii=False, indent=2)
    print(f" -> data/cluster_data.json ({len(clusters)} clusters)")

    # ---- 任务7: CF推荐 + 搜索索引 ----
    print("Building CF search index...")
    cf_df = pd.read_csv("data/cf_recommendations.csv", encoding="utf-8-sig")

    # 构建装备中文→英文反向查找（用于颜色分类）
    item_cn_to_en = {v: k for k, v in ITEM_CN.items()}

    # 每个棋子的总出场次数
    champ_total = cf_df.groupby("棋子")["出场次数"].sum().to_dict()

    # 每个棋子的装备详情
    champ_items = defaultdict(list)
    for _, row in cf_df.iterrows():
        item_name_cn = str(row["装备"])  # CSV中已是中文名
        # 通过反向查找获取英文名用于颜色分类
        item_en = item_cn_to_en.get(item_name_cn, item_name_cn)
        color = equip_color(item_en)
        champ_items[row["棋子"]].append({
            "rank": int(row["排名"]),
            "itemCn": item_name_cn,
            "top4": str(row["前四率"]),
            "games": int(row["出场次数"]),
            "avgPlace": round(float(row["平均排名"]), 2) if "平均排名" in cf_df.columns and pd.notna(row.get("平均排名")) else None,
            "score": round(float(row["CF得分"]), 2),
            "color": color,
        })

    # 搜索索引: 英文名→中文名, 中文名→中文名
    search_index = {}
    for api_name, cn_name in CHAMP_CN.items():
        search_index[api_name] = cn_name
        search_index[api_name.lower()] = cn_name
        search_index[cn_name] = cn_name

    cf_json = {
        "champItems": {k: v for k, v in champ_items.items()},
        "champTotal": {k: int(v) for k, v in champ_total.items()},
        "searchIndex": search_index,
    }

    with open("data/cf_data.json", "w", encoding="utf-8") as f:
        json.dump(cf_json, f, ensure_ascii=False, indent=2)

    champ_count = len(champ_items)
    item_count = len(set(r["itemCn"] for items in champ_items.values() for r in items))
    print(f" -> data/cf_data.json ({champ_count} champs, {item_count} items)")

    print("\nDone! JSON data ready for web page.")


if __name__ == "__main__":
    main()
