"""
任务5：K-Means 聚类发现 Meta 阵容
用无监督学习方法自动识别当前版本的主流强势阵容
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from config import TRAITS, CHAMPIONS

# 中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 手动命名的10个簇（用于语义标注）
CLUSTER_NAMES = {
    0: "阵容0",
    1: "阵容1",
    2: "阵容2",
    3: "阵容3",
    4: "阵容4",
    5: "阵容5",
    6: "阵容6",
    7: "阵容7",
    8: "阵容8",
    9: "阵容9",
}


def load_data(path="data/tft_dump.parquet"):
    df = pd.read_parquet(path)
    print(f"加载数据集: {len(df)} 条记录, {df['match_id'].nunique()} 局游戏")
    return df


def run_clustering(df, k=10):
    """对阵容进行K-Means聚类（仅使用羁绊特征）"""
    # 提取羁绊列（syn_开头）
    synergy_cols = [c for c in df.columns if c.startswith("syn_")]
    X = df[synergy_cols].fillna(0).values

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"\nK-Means 聚类: K={k}, 特征维度={X_scaled.shape[1]} (羁绊数)")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
    df["cluster"] = kmeans.fit_predict(X_scaled)

    return df, X_scaled, kmeans


def analyze_clusters(df, synergy_cols, champion_cols):
    """分析每个簇的统计信息：样本量、前四率、核心羁绊、核心棋子"""
    print("\n" + "=" * 70)
    print("  Meta 阵容发现结果 (K-Means 聚类)")
    print("=" * 70)

    for cid in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cid]
        n_players = len(subset)
        winrate = subset["win"].mean() * 100
        avg_place = subset["placement"].mean()
        name = CLUSTER_NAMES.get(cid, f"阵容{cid}")

        # 核心羁绊（该簇内平均等级最高的4个）
        syn_mean = subset[synergy_cols].mean().sort_values(ascending=False)
        top4_syn = syn_mean.head(4)

        # 核心棋子（该簇内出现率最高的5个）
        unit_mean = subset[champion_cols].mean().sort_values(ascending=False)
        top5_units = unit_mean.head(5)

        print(f"\n■ 簇 {cid}: {name} [{n_players}名玩家]")
        print(f"  前四率: {winrate:.1f}%  |  平均排名: {avg_place:.2f}")
        print(f"  核心羁绊:")
        for trait_col, val in top4_syn.items():
            trait_name = TRAITS.get(trait_col.replace("syn_", ""), trait_col)
            pct = (subset[trait_col] > 0).mean() * 100
            print(f"    - {trait_name:<12} 平均等级 {val:.1f} (携带率 {pct:.0f}%)")
        print(f"  核心棋子:")
        for unit_col, val in top5_units.items():
            unit_info = CHAMPIONS.get(unit_col.replace("unit_", ""), None)
            unit_name = unit_info[0] if unit_info else unit_col
            print(f"    - {unit_name:<12} 出场率 {val*100:.0f}%")

    return df


def plot_cluster_winrates(df, save_path="figures/clustering_winrates.png"):
    """图1：各簇前四率柱状图"""
    winrates = df.groupby("cluster")["win"].mean() * 100
    names = [CLUSTER_NAMES.get(c, f"簇{c}") for c in winrates.index]

    sorted_idx = np.argsort(winrates.values)[::-1]
    wr_sorted = winrates.values[sorted_idx]
    names_sorted = [names[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#17C25E" if w >= 50 else "#e74c3c" for w in wr_sorted]
    bars = ax.bar(range(len(wr_sorted)), wr_sorted, color=colors, edgecolor="black", linewidth=0.5)

    for bar, val in zip(bars, wr_sorted):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

    ax.axhline(y=50, color="black", linestyle="--", linewidth=2, label="平均线 (50%)")
    ax.set_xticks(range(len(wr_sorted)))
    ax.set_xticklabels(names_sorted, rotation=30, ha="right", fontsize=11)
    ax.set_ylabel("前四率 (%)", fontsize=13)
    ax.set_title("各Meta阵容前四率对比 (K-Means 聚类结果)", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(wr_sorted) + 10)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"\n[图表保存] {save_path}")


def plot_cluster_pca(X_scaled, df, save_paths, k_values=[8, 9, 10]):
    """图2：不同K值下的PCA可视化"""
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, k in zip(axes, k_values):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(X_scaled)
        scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels,
                             cmap="tab10", s=8, alpha=0.7)
        ax.set_title(f"K-Means (K = {k})", fontsize=13, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle("不同K值下的阵容聚类效果 (PCA降维可视化)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = save_paths.get("pca", "figures/clustering_pca.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"[图表保存] {path}")


def plot_cluster_size_distribution(df, save_path="figures/cluster_sizes.png"):
    """图3：各簇样本量分布"""
    sizes = df["cluster"].value_counts().sort_index()
    names = [CLUSTER_NAMES.get(c, f"簇{c}") for c in sizes.index]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
    wedges, texts, autotexts = ax.pie(
        sizes.values, labels=names, autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.85
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("各阵容簇分布占比", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[图表保存] {save_path}")


def main():
    # 1. 加载数据
    df = load_data()

    # 2. 提取特征列
    synergy_cols = [c for c in df.columns if c.startswith("syn_")]
    champion_cols = [c for c in df.columns if c.startswith("unit_")]

    # 3. 聚类
    df, X_scaled, kmeans = run_clustering(df, k=10)

    # 4. 分析
    df = analyze_clusters(df, synergy_cols, champion_cols)

    # 5. 可视化
    plot_cluster_winrates(df)
    plot_cluster_pca(X_scaled, df, {"pca": "figures/clustering_pca.png"})
    plot_cluster_size_distribution(df)

    print("\n" + "=" * 70)
    print("  聚类任务完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
