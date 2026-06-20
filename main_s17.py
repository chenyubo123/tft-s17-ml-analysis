"""
TFT S17 星神赛季 —— 机器学习分析
任务5: K-Means 聚类发现 Meta 阵容
任务7: 装备最优分配 (BIS)
数据源: Riot API 韩服王者/宗师/大师
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import os

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================
#  数据加载 & 预处理
# ============================================
def load_and_clean():
    df = pd.read_parquet("data/tft_dump.parquet")
    print(f"加载数据集: {len(df)} 条记录, {df['match_id'].nunique()} 局游戏")

    # 过滤: 只保留真实英雄棋子 (排除 PVE/Event/Enemy/Summon)
    unit_cols_all = [c for c in df.columns if c.startswith("unit_TFT17_")]
    exclude = ["PVE", "Enemy", "Summon", "Minion"]
    unit_cols = []
    for c in unit_cols_all:
        if not any(ex in c for ex in exclude):
            unit_cols.append(c)

    # 羁绊列
    trait_cols = [c for c in df.columns if c.startswith("syn_TFT17_")]

    # 过滤: 每条记录至少携带1个真实棋子
    df_filtered = df[df[unit_cols].sum(axis=1) > 0].copy()
    print(f"过滤后: {len(df_filtered)} 条记录")
    print(f"棋子种类: {len(unit_cols)}, 羁绊种类: {len(trait_cols)}")

    return df_filtered, unit_cols, trait_cols


# ============================================
#  工具函数: 从列名解出棋子名/羁绊名
# ============================================
def strip_unit_name(col):
    """unit_TFT17_Garen -> Garen"""
    name = col.replace("unit_TFT17_", "")
    return name

def strip_trait_name(col):
    """syn_TFT17_DarkStar -> DarkStar"""
    name = col.replace("syn_TFT17_", "")
    return name

def strip_item_champion(col):
    """item_TFT_Item_RabadonsDeathcap_TFT17_Nami -> (RabadonsDeathcap, Nami)"""
    # 格式: item_TFT_Item_ItemName_TFT17_ChampionName  或 item_TFT17_Item_...
    parts = col.split("_")
    # 找 ItemName: 从 item_ 之后到 TFT17_ 之前
    try:
        tft17_idx = next(i for i, p in enumerate(parts) if p == "TFT17")
        item_parts = parts[parts.index("Item")+1:tft17_idx] if "Item" in parts else parts[1:tft17_idx]
        item_name = "_".join(item_parts)
        champ_name = parts[tft17_idx + 1]
        return item_name, champ_name
    except (StopIteration, ValueError, IndexError):
        return None, None


# ============================================
#  任务5: K-Means 聚类
# ============================================
def task5_clustering(df, trait_cols, unit_cols):
    print("\n" + "=" * 60)
    print("  任务5: K-Means 聚类 —— 发现 Meta 阵容")
    print("=" * 60)

    X = df[trait_cols].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"特征维度: {X_scaled.shape[1]} 羁绊, 样本数: {X_scaled.shape[0]}")

    kmeans = KMeans(n_clusters=10, random_state=42, n_init="auto")
    df["cluster"] = kmeans.fit_predict(X_scaled)

    # --- 分析每个簇 ---
    for cid in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cid]
        n = len(sub)
        wr = sub["win"].mean() * 100
        avg = sub["placement"].mean()

        # 核心羁绊 (top 4 by mean)
        syn_mean = sub[trait_cols].mean().sort_values(ascending=False).head(4)
        # 核心棋子 (top 5 by mean count)
        unit_mean = sub[unit_cols].mean().sort_values(ascending=False).head(5)

        print(f"\n[簇 {cid}] 玩家数: {n}, 前四率: {wr:.1f}%, 平均排名: {avg:.2f}")
        print("  核心羁绊:")
        for tc, val in syn_mean.items():
            pct = (sub[tc] > 0).mean() * 100
            print(f"    {strip_trait_name(tc):<20} avg={val:.1f}  ({pct:.0f}%)")
        print("  核心棋子:")
        for uc, val in unit_mean.items():
            print(f"    {strip_unit_name(uc):<15}  avg星级={val:.1f}  ({sub[uc].gt(0).mean()*100:.0f}%)")

    # --- 图1: 前四率柱状图 ---
    wr_by_cluster = df.groupby("cluster")["win"].mean() * 100
    wr_sorted = wr_by_cluster.sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#17C25E" if w >= 50 else "#e74c3c" for w in wr_sorted.values]
    bars = ax.bar(range(len(wr_sorted)), wr_sorted.values, color=colors, edgecolor="black")
    for bar, v in zip(bars, wr_sorted.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.5,
                f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")
    ax.axhline(y=50, color="black", linestyle="--", label="50% baseline")
    ax.set_xticks(range(len(wr_sorted)))
    ax.set_xticklabels([f"Cluster {c}" for c in wr_sorted.index], rotation=30, ha="right")
    ax.set_ylabel("Top 4 Rate (%)", fontsize=13)
    ax.set_title("S17 Meta Compositions - Top 4 Rate (K-Means, K=10)", fontsize=14, fontweight="bold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/clustering_winrates.png", dpi=300)
    plt.close()
    print(f"\n[图表] {FIG_DIR}/clustering_winrates.png")

    # --- 图2: PCA ---
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax_, k in zip(axes, [8, 9, 10]):
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        labels = km.fit_predict(X_scaled)
        ax_.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="tab10", s=5, alpha=0.7)
        ax_.set_title(f"K = {k}")
        ax_.set_xticks([]); ax_.set_yticks([])
    fig.suptitle("PCA Visualization of S17 Compositions", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/clustering_pca.png", dpi=300)
    plt.close()
    print(f"[图表] {FIG_DIR}/clustering_pca.png")

    # --- 图3: 簇大小饼图 ---
    sizes = df["cluster"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = ax.pie(
        sizes.values, labels=[f"C{c}" for c in sizes.index],
        autopct="%1.1f%%", colors=plt.cm.Set3(np.linspace(0, 1, len(sizes))),
        startangle=90
    )
    ax.set_title("Cluster Size Distribution", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/cluster_sizes.png", dpi=300)
    plt.close()
    print(f"[图表] {FIG_DIR}/cluster_sizes.png")

    return df, kmeans


# ============================================
#  任务7: BIS 装备推荐 (线性回归)
# ============================================
def task7_bis(df, unit_cols):
    print("\n" + "=" * 60)
    print("  任务7: 线性回归 —— 装备最优分配 (BIS)")
    print("=" * 60)

    # 构建特征矩阵: champion x item 组合
    item_cols_all = [c for c in df.columns if c.startswith("item_")]
    
    # 只保留出现足够多次的组合 (>= 30)
    col_means = df[item_cols_all].replace(0, np.nan).mean()
    valid_cols = [c for c in item_cols_all if col_means[c] * len(df) >= 30]
    
    X = df[valid_cols].fillna(0).astype(float)
    y = df["placement"].values.astype(float)
    
    print(f"特征维度: {len(valid_cols)} (出现>=30次的棋子-装备组合)")
    
    # 训练线性回归
    model = LinearRegression()
    model.fit(X, y)
    print(f"R^2 = {model.score(X, y):.4f}")
    print("Neg coeff = better item, Pos coeff = worse item")

    # 筛选热门棋子做BIS分析 (出场率 > 20%)
    unit_rates = {uc: (df[uc] > 0).mean() for uc in unit_cols}
    popular = sorted(unit_rates.items(), key=lambda x: x[1], reverse=True)[:6]

    champion_coeffs = {}
    for uc, _ in popular:
        u_name = strip_unit_name(uc)
        cols_for_this = [c for c in valid_cols if f"TFT17_{u_name}" in c]
        if len(cols_for_this) < 2:
            continue
        
        idxs = [list(X.columns).index(c) for c in cols_for_this]
        col_names = []
        item_names = []
        deltas = []
        for c, idx in zip(cols_for_this, idxs):
            iname, _ = strip_item_champion(c)
            if iname:
                col_names.append(c)
                item_names.append(iname)
                deltas.append(model.coef_[idx])

        # 排序: delta越小越好
        sorted_data = sorted(zip(item_names, deltas), key=lambda x: x[1])
        champion_coeffs[u_name] = {"data": sorted_data, "cols": col_names}

        print(f"\n[{u_name}] BIS 分析:")
        for iname, delta in sorted_data[:5]:
            print(f"  {iname:<30} delta={delta:+.4f}")
        top3 = [x[0] for x in sorted_data[:3]]
        print(f"  Recommended: {' + '.join(top3)}")

    # --- 图表: BIS 横向对比 ---
    if champion_coeffs:
        fig, axes = plt.subplots(len(champion_coeffs), 1, figsize=(12, 3 * len(champion_coeffs)))
        if len(champion_coeffs) == 1:
            axes = [axes]
        for ax, (u_name, info) in zip(axes, champion_coeffs.items()):
            data = info["data"]
            names = [x[0] for x in data]
            vals = [x[1] for x in data]
            colors = ["#17C25E" if v < 0 else "#e74c3c" for v in vals]
            ax.barh(range(len(names)), vals, color=colors, edgecolor="black")
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels(names, fontsize=9)
            ax.set_xlabel("Delta (neg = better)")
            ax.set_title(f"{u_name}")
            ax.axvline(x=0, color="black", linestyle="--")
            ax.invert_yaxis()
        plt.tight_layout()
        path = f"{FIG_DIR}/bis_comparison.png"
        plt.savefig(path, dpi=300)
        plt.close()
        print(f"\n[图表] {path}")

    return model


# ============================================
#  主流程
# ============================================
def main():
    print("=" * 56)
    print("  TFT S17 星神赛季 - 机器学习分析")
    print("  数据: Riot API 韩服 Challenger/GM/Master")
    print("=" * 56)

    df, unit_cols, trait_cols = load_and_clean()

    # 任务5: 聚类
    df, _ = task5_clustering(df, trait_cols, unit_cols)

    # 任务7: BIS
    task7_bis(df, unit_cols)

    print("\n" + "=" * 56)
    print("  全部分析完成！")
    print("=" * 56)


if __name__ == "__main__":
    main()
