"""
任务7：装备最优分配 —— BIS (Best-in-Slot) 装备推荐
用线性回归分析每件装备对排名的边际效应，为棋子推荐最佳三件套
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from config import CHAMPIONS, ITEMS

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

TARGET_CHAMPIONS = ["TFT9_Garen", "TFT9_Azir", "TFT9_Darius", "TFT9_Yasuo"]


def load_data(path="data/tft_dump.parquet"):
    return pd.read_parquet(path)


def prepare_feature_matrix(df):
    """构建特征矩阵 X (champion_with_item 组合) 和目标 y (排名)"""
    # 只保留 champion_with_item 列作为特征
    item_cols = [c for c in df.columns if "_with_" in c]
    X = df[item_cols].fillna(0).astype(float)
    y = df["placement"].values.astype(float)

    # 过滤掉全是0的装备组合（从未出现过）
    nonzero_cols = X.columns[(X.sum(axis=0) > 30)]
    X = X[nonzero_cols]

    print(f"特征矩阵: {X.shape[1]} 维 (出现>30次的棋子-装备组合)")
    return X, y


def train_linear_regression(X, y):
    """训练线性回归模型，提取装备的 Delta 系数"""
    model = LinearRegression()
    model.fit(X, y)

    coeffs = pd.DataFrame({
        "variable": X.columns,
        "delta": model.coef_
    }).sort_values("delta")

    print(f"\n模型 R^2 = {model.score(X, y):.4f}")
    print(f"Delta 解释: 负值 = 降低排名 (更好), 正值 = 提高排名 (更差)")
    return model, coeffs


def analyze_bis_for_champion(coeffs, champion_api, top_n=5):
    """为指定棋子分析最佳和最差装备"""
    champ_info = CHAMPIONS.get(champion_api, None)
    champ_name = champ_info[0] if champ_info else champion_api

    # 筛选该棋子的所有装备组合
    mask = coeffs["variable"].str.contains(f"{champion_api}_with_")
    champ_coeffs = coeffs[mask].copy()

    if champ_coeffs.empty:
        print(f"\n[警告] 数据中未找到 {champ_name} 的装备记录")
        return None

    # 提取装备名
    champ_coeffs["item_name"] = champ_coeffs["variable"].apply(
        lambda v: ITEMS.get(v.split("_with_")[-1], v.split("_with_")[-1])
    )

    # 按 Delta 排序（负值越好）
    champ_coeffs = champ_coeffs.sort_values("delta")

    print(f"\n{'=' * 60}")
    print(f"  [{champ_name}] 装备最优分析")
    print(f"{'=' * 60}")

    print(f"\n  [最佳装备] (前{top_n}):")
    for _, row in champ_coeffs.head(top_n).iterrows():
        print(f"    {row['item_name']:<12}  Δ = {row['delta']:.3f}")

    bis = champ_coeffs.head(3)
    print(f"\n  → 推荐三件套: {bis['item_name'].iloc[0]} + {bis['item_name'].iloc[1]} + {bis['item_name'].iloc[2]}")

    print(f"\n  [最差装备] (后{top_n}):")
    for _, row in champ_coeffs.tail(top_n).iloc[::-1].iterrows():
        print(f"    {row['item_name']:<12}  Δ = {row['delta']:.3f}")

    return champ_coeffs


def plot_bis_horizontal(champ_coeffs, champion_api, save_path):
    """水平条形图：装备Delta值"""
    champ_info = CHAMPIONS.get(champion_api, None)
    champ_name = champ_info[0] if champ_info else champion_api

    data = champ_coeffs.sort_values("delta", ascending=True)
    # 取前8和后4
    top8 = data.head(8)
    bottom4 = data.tail(4)
    plot_data = pd.concat([bottom4, top8])

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#e74c3c" if d >= 0 else "#17C25E" for d in plot_data["delta"]]
    ax.barh(plot_data["item_name"], plot_data["delta"], color=colors, edgecolor="black", linewidth=0.5)
    ax.axvline(x=0, color="black", linewidth=1.5)

    for i, (_, row) in enumerate(plot_data.iterrows()):
        x_pos = row["delta"] + (0.02 if row["delta"] >= 0 else -0.02)
        ha = "left" if row["delta"] >= 0 else "right"
        ax.text(x_pos, i, f"{row['delta']:.3f}", va="center", ha=ha, fontsize=9, fontweight="bold")
        ax.text(min(plot_data["delta"]) - 0.03, i,
                f"[推荐]" if row['delta'] < 0 else "[不推荐]",
                va="center", ha="right", fontsize=8, color="gray")

    ax.set_title(f"{champ_name} 装备 Delta 分析\n(负值 = 降低排名/更强)", fontsize=14, fontweight="bold")
    ax.set_xlabel("对排名的影响 (Δ)", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[图表保存] {save_path}")


def plot_bis_comparison(all_results, save_path="figures/bis_comparison.png"):
    """多个棋子的BIS对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for ax, (champ_api, champ_coeffs) in zip(axes, all_results.items()):
        data = champ_coeffs.sort_values("delta").head(6)
        colors = ["#17C25E" if d < 0 else "#e74c3c" for d in data["delta"]]
        ax.bar(data["item_name"], data["delta"], color=colors, edgecolor="black", linewidth=0.5)
        ax.axhline(y=0, color="black", linewidth=1)
        champ_info = CHAMPIONS.get(champ_api, None)
        ax.set_title(champ_info[0] if champ_info else champ_api, fontsize=13, fontweight="bold")
        ax.set_ylabel("Δ (对排名影响)", fontsize=11)
        ax.tick_params(axis="x", rotation=30, labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.suptitle("多名英雄装备 Delta 对比", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[图表保存] {save_path}")


def main():
    df = load_data()
    X, y = prepare_feature_matrix(df)
    model, coeffs = train_linear_regression(X, y)

    # 分析多个棋子的BIS
    all_results = {}
    for champ_api in TARGET_CHAMPIONS:
        result = analyze_bis_for_champion(coeffs, champ_api)
        if result is not None:
            all_results[champ_api] = result

    # 为每个棋子保存单独图表
    for champ_api, champ_coeffs in all_results.items():
        save_name = champ_api.replace("TFT9_", "").lower()
        plot_bis_horizontal(champ_coeffs, champ_api,
                           f"figures/bis_{save_name}.png")

    # 合并对比图
    plot_bis_comparison(all_results)

    print("\n" + "=" * 60)
    print("  装备推荐任务完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
