"""
任务7 v2: 协同过滤 —— 棋子与装备搭配推荐
方法: Item-Based Collaborative Filtering
  1. 构建 棋子×装备 胜率矩阵 (champion-item matrix)
  2. 计算棋子间余弦相似度 (装备使用模式相近的棋子互相参考)
  3. 综合打分 = 0.7×直接胜率 + 0.3×相似棋子加权推荐
  4. 输出每棋子推荐三件套 + 可视化热力图
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import os

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

# 散件（不参与推荐）
COMPONENTS = {
    "BFSword", "ChainVest", "GiantsBelt", "NeedlesslyLargeRod",
    "NegatronCloak", "RecurveBow", "SparringGloves", "TearOfTheGoddess",
    "Spatula", "FryingPan", "TacticiansRing", "TacticiansScepter",
    "EmptyBag", "GlacialMallet",
}

# S17 棋子中文名映射
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

# 装备中文名映射 (S17星神赛季 37件可合成装备)
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
    # 以下两件tactics.tools有收录但实战出场率接近0%，注意验证
    "Anomaly": "异常突变",
    # Artifacts
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
    # Ornn items
    "OrnnDeathsDefiance": "死亡之蔑", "OrnnHorizonFocus": "视界专注",
    "OrnnHullbreaker": "破舰者", "OrnnInfinityForce": "无限之力",
    "OrnnTheCollector": "收集者", "OrnnZhonyasParadox": "中娅悖论",
    # Special
    "ForceOfNature": "自然之力", "CrownOfDemacia": "德玛西亚王冠",
    "LavenderCrown": "薰衣草王冠", "ShimmerscaleCrownOfChampions": "冠军王冠",
    "ShimmerscaleDravensAxe": "德莱文之斧",
    "ShimmerscaleGamblersBlade": "赌徒之刃",
    "ShimmerscaleGoldmancersStaff": "金魔法杖",
    "ShimmerscaleMogulsMail": "大亨之铠",
    "SevikasJinxedArm": "塞薇卡的诅咒臂铠",
}


def parse_item_col(col):
    """item_TFT_Item_GuinsoosRageblade_TFT17_Aatrox -> (item_name, champ_name)"""
    parts = col.split("_")
    try:
        tft17_idx = next(i for i, p in enumerate(parts) if p == "TFT17")
        item_start = next(i for i, p in enumerate(parts) if p == "Item") + 1
        item_name = "_".join(parts[item_start:tft17_idx])
        champ_name = parts[tft17_idx + 1]
        return item_name, champ_name
    except (StopIteration, ValueError, IndexError):
        return None, None


def name_item(item_id):
    """装备ID -> 中文名"""
    base = item_id.replace("Radiant", "")
    if base in ITEM_CN:
        cn = ITEM_CN[base]
        return cn + "(光明)" if "Radiant" in item_id else cn
    return item_id


def name_champ(champ_id):
    """棋子ID -> 中文名"""
    return CHAMP_CN.get(champ_id, champ_id)


def is_valid_item(item_id):
    """过滤：排除散件、排除空名、排除非S17装备（白名单校验）"""
    if not item_id:
        return False
    base = item_id.replace("Radiant", "")
    if base in COMPONENTS:
        return False
    if base not in ITEM_CN:
        return False
    return True


def load_and_build_matrix():
    """加载数据，构建 棋子×装备 统计矩阵"""
    print("=" * 60)
    print("  协同过滤 —— 棋子×装备 矩阵构建")
    print("=" * 60)

    df = pd.read_parquet("data/tft_dump.parquet")
    item_cols = [c for c in df.columns if c.startswith("item_")]

    # {(champ, item): [placements]}
    stats = defaultdict(list)

    for _, row in df.iterrows():
        placement = row["placement"]
        for col in item_cols:
            if row[col] != 1:
                continue
            item_name, champ_name = parse_item_col(col)
            if item_name and champ_name and is_valid_item(item_name):
                # 把 Radiant 版合并到普通版
                base_item = item_name.replace("Radiant", "")
                stats[(champ_name, base_item)].append(placement)

    # 转为 DataFrame
    records = []
    for (champ, item), placements in stats.items():
        n = len(placements)
        if n < 8:
            continue
        arr = np.array(placements)
        records.append({
            "champion": champ,
            "item": item,
            "games": n,
            "avg_placement": arr.mean(),
            "top4_rate": (arr <= 4).mean(),
            "top1_rate": (arr == 1).mean(),
        })

    mat_df = pd.DataFrame(records)
    print(f"  有效棋子数: {mat_df['champion'].nunique()}")
    print(f"  有效装备数: {mat_df['item'].nunique()}")
    print(f"  总棋子-装备组合: {len(mat_df)}")

    return mat_df, df


def compute_champion_similarity(mat_df):
    """计算棋子相似度（基于装备使用模式）"""
    print("\n" + "=" * 60)
    print("  计算棋子相似度矩阵 (Cosine)")

    # 构建 棋子×装备 的 top4_rate 矩阵
    pivot = mat_df.pivot_table(
        index="champion", columns="item", values="top4_rate", aggfunc="mean"
    ).fillna(0.5)  # 未出现过的装备给0.5基准

    champs = pivot.index.tolist()
    X = pivot.values

    sim_matrix = cosine_similarity(X)
    sim_df = pd.DataFrame(sim_matrix, index=champs, columns=champs)

    print(f"  相似度矩阵: {len(champs)} × {len(champs)}")
    return sim_df, pivot


def recommend_with_cf(mat_df, sim_df, pivot, alpha=0.7, min_games=10):
    """
    协同过滤推荐
    alpha: 直接胜率的权重 (剩余 (1-alpha) 给CF邻居)
    """
    print("\n" + "=" * 60)
    print(f"  协同过滤推荐 (直接权重={alpha}, CF邻居权重={1-alpha})")
    print("=" * 60)

    champion_scores = mat_df.copy()

    # Step 1: 计算每个(champion, item)的直接得分
    # score_direct = top4_rate * log(games)  —— 胜率高 + 样本量大 = 得分高
    champion_scores["score_direct"] = (
        champion_scores["top4_rate"] * np.log1p(champion_scores["games"])
    )

    # Step 2: 对每个(champion, item)加上CF邻居得分
    cf_scores = []
    for _, row in champion_scores.iterrows():
        champ = row["champion"]
        item = row["item"]

        # 找 top-5 最相似棋子
        if champ in sim_df.index:
            neighbors = sim_df.loc[champ].drop(champ).nlargest(5)
            cf_sum = 0.0
            cf_weight = 0.0
            for n_champ, sim in neighbors.items():
                if sim < 0.1:
                    continue
                n_data = pivot.loc[n_champ, item] if item in pivot.columns else 0.5
                cf_sum += sim * n_data
                cf_weight += sim
            cf_score = cf_sum / cf_weight if cf_weight > 0 else champion_scores["top4_rate"].mean()
        else:
            cf_score = 0.5

        cf_scores.append(cf_score)

    champion_scores["score_cf"] = cf_scores

    # 综合得分
    champion_scores["score_final"] = (
        alpha * champion_scores["score_direct"]
        + (1 - alpha) * champion_scores["score_cf"] * np.log1p(champion_scores["games"])
    )

    return champion_scores


def recommend_top3(scores_df, min_games=10):
    """为每个棋子输出推荐三件套"""
    # 只考虑出场够多的棋子（>=30局出现）
    champ_popularity = scores_df.groupby("champion")["games"].sum()
    popular_champs = champ_popularity[champ_popularity >= 30].index

    results = {}
    for champ in popular_champs:
        champ_data = scores_df[
            (scores_df["champion"] == champ) & (scores_df["games"] >= min_games)
        ].sort_values("score_final", ascending=False)

        if len(champ_data) < 3:
            continue

        top3 = champ_data.head(3)
        results[champ] = {
            "items": [(name_item(r["item"]), r["top4_rate"], r["games"], r["score_final"])
                       for _, r in top3.iterrows()],
            "avg_top4": champ_data.head(1)["top4_rate"].values[0],
        }

    return results


def print_recommendations(results):
    """输出推荐结果"""
    print("\n" + "=" * 60)
    print("  S17 棋子装备推荐（协同过滤）")
    print("=" * 60)

    # 按最高胜率排序
    sorted_champs = sorted(results.items(), key=lambda x: x[1]["avg_top4"], reverse=True)

    for champ, info in sorted_champs:
        cn = name_champ(champ)
        print(f"\n  [{cn}]  最佳装备率={info['avg_top4']:.1%}")
        for i, (item_cn, wr, games, score) in enumerate(info["items"], 1):
            print(f"    {i}. {item_cn:<16} 前四率={wr:.1%}  出场={games}局  CF分={score:.3f}")

    return sorted_champs


def plot_heatmap(mat_df, top_champs=20, top_items=25):
    """热力图：棋子×装备 胜率矩阵"""
    print(f"\n[图表] 热力图...")

    # 选出场最多的棋子和装备
    champ_games = mat_df.groupby("champion")["games"].sum().nlargest(top_champs)
    item_games = mat_df.groupby("item")["games"].sum().nlargest(top_items)

    pivot = mat_df.pivot_table(
        index="champion", columns="item", values="top4_rate", aggfunc="mean"
    )
    pivot = pivot.loc[champ_games.index, item_games.index]

    # 用中文名
    pivot.index = [name_champ(c) for c in pivot.index]
    pivot.columns = [name_item(c) for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(22, 12))
    im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto", vmin=0.2, vmax=0.8)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)

    # 标注数值
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                color = "white" if val < 0.3 or val > 0.7 else "black"
                ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=6, color=color)

    plt.colorbar(im, ax=ax, label="前四率 (Top4 Rate)")
    ax.set_title("S17 云顶之弈 棋子×装备 前四率热力图\n(绿色=高胜率装备, 红色=低胜率装备)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = f"{FIG_DIR}/cf_heatmap.png"
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  -> {path}")


def plot_champion_recommendations(results, top_n=12):
    """为热门棋子绘制推荐卡片"""
    print(f"[图表] 棋子推荐卡片...")

    sorted_champs = sorted(results.items(), key=lambda x: x[1]["avg_top4"], reverse=True)[:top_n]

    fig, axes = plt.subplots(3, 4, figsize=(20, 15))
    axes = axes.flatten()

    for ax, (champ, info) in zip(axes, sorted_champs):
        items = info["items"]
        names = [x[0] for x in items]
        wrs = [x[1] for x in items]
        games = [x[2] for x in items]

        colors = ["#17C25E" if wr >= 0.55 else "#f39c12" if wr >= 0.50 else "#e74c3c"
                  for wr in wrs]

        bars = ax.barh(range(len(names))[::-1], wrs, color=colors, edgecolor="black", linewidth=0.5)
        ax.set_yticks(range(len(names))[::-1])
        ax.set_yticklabels(names, fontsize=9)

        for i, (bar, wr_, g) in enumerate(zip(bars, wrs, games)):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{wr_:.0%} (n={g})", va="center", fontsize=8, fontweight="bold")

        ax.set_xlim(0, max(wrs) * 1.35 if max(wrs) > 0 else 1)
        ax.set_title(name_champ(champ), fontsize=12, fontweight="bold")
        ax.axvline(x=0.5, color="gray", linestyle="--", alpha=0.5)
        ax.set_xlabel("前四率")

    fig.suptitle("S17 棋子推荐三件套 (协同过滤)\n绿色=强力推荐, 橙色=可用, 红色=备选",
                 fontsize=16, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = f"{FIG_DIR}/cf_recommendations.png"
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  -> {path}")


def plot_similarity_network(sim_df, top_champs=15):
    """棋子相似度网络图（用热力图形式呈现）"""
    print(f"[图表] 棋子相似度热力图...")

    champs = sim_df.index[:top_champs]
    sub_sim = sim_df.loc[champs, champs]

    labels = [name_champ(c) for c in champs]

    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(sub_sim.values, cmap="YlOrRd", vmin=0, vmax=1)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)

    for i in range(len(labels)):
        for j in range(len(labels)):
            if i != j:
                val = sub_sim.values[i, j]
                if val > 0.3:
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            fontsize=6, color="white" if val > 0.7 else "black")

    plt.colorbar(im, ax=ax, label="余弦相似度")
    ax.set_title("S17 棋子相似度热力图\n(基于装备使用模式的余弦相似度)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = f"{FIG_DIR}/cf_similarity.png"
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  -> {path}")


def main():
    print("\n" + "=" * 60)
    print("  TFT S17 协同过滤 —— 装备推荐系统")
    print("  数据: Riot API 韩服 496局真实对局")
    print("=" * 60)

    # 1. 加载 & 构建矩阵
    mat_df, raw_df = load_and_build_matrix()

    # 2. 棋子相似度
    sim_df, pivot = compute_champion_similarity(mat_df)

    # 3. 协同过滤推荐
    scores_df = recommend_with_cf(mat_df, sim_df, pivot, alpha=0.7, min_games=10)

    # 4. 为每个棋子推荐三件套
    results = recommend_top3(scores_df, min_games=10)
    sorted_champs = print_recommendations(results)

    # 5. 可视化
    plot_heatmap(mat_df, top_champs=30, top_items=40)
    plot_champion_recommendations(results, top_n=12)
    plot_similarity_network(sim_df, top_champs=20)

    # 6. 导出推荐表（CSV给网页和报告用）
    export_csv = []
    champ_popularity = scores_df.groupby("champion")["games"].sum()
    popular_champs = champ_popularity[champ_popularity >= 30].index
    for champ in popular_champs:
        cn = name_champ(champ)
        champ_data = scores_df[
            (scores_df["champion"] == champ) & (scores_df["games"] >= 10)
        ].sort_values("score_final", ascending=False)
        top3 = champ_data.head(3)
        for i, (_, r) in enumerate(top3.iterrows(), 1):
            export_csv.append({
                "棋子": cn, "装备": name_item(r["item"]), "排名": i,
                "前四率": f"{r['top4_rate']:.1%}", "出场次数": int(r["games"]),
                "平均排名": round(float(r["avg_placement"]), 2),
                "CF得分": f"{r['score_final']:.3f}"
            })
    pd.DataFrame(export_csv).to_csv("data/cf_recommendations.csv", index=False, encoding="utf-8-sig")
    print(f"\n[导出] data/cf_recommendations.csv")

    print("\n" + "=" * 60)
    print("  协同过滤装备推荐完成！")
    print(f"  图表: {FIG_DIR}/cf_*.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
