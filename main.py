"""
TFT 云顶之弈机器学习分析 —— 主入口
运行顺序: 数据生成 → 聚类分析(任务5) → 装备推荐(任务7)
"""

import os
import sys
from data_generator import generate_matches, add_macro_features, clean_data
from clustering import load_data as cl_load, run_clustering, analyze_clusters, \
    plot_cluster_winrates, plot_cluster_pca, plot_cluster_size_distribution
from bis_item import load_data as bis_load, prepare_feature_matrix, \
    train_linear_regression, analyze_bis_for_champion, \
    plot_bis_horizontal, plot_bis_comparison

# 目标棋子（用于BIS分析）
TARGET_CHAMPIONS = ["TFT9_Garen", "TFT9_Azir", "TFT9_Darius", "TFT9_Yasuo"]


def step1_generate_data():
    """第1步：生成模拟对局数据"""
    print("=" * 60)
    print("  第1步：生成 TFT 对局数据")
    print("=" * 60)

    if os.path.exists("data/tft_dump.parquet"):
        resp = input("\n数据文件已存在，重新生成吗？(y/N): ").strip().lower()
        if resp != "y":
            print("跳过数据生成，使用已有数据")
            return

    df = generate_matches(n_matches=500)
    df = add_macro_features(df)
    df = clean_data(df)
    df.to_parquet("data/tft_dump.parquet", index=False)
    print(f"\n[完成] 数据集: {len(df)} 行, ~{df['win'].mean()*100:.1f}% 前四率\n")


def step2_clustering():
    """第2步：K-Means 聚类发现 Meta 阵容"""
    print("\n" + "=" * 60)
    print("  第2步：K-Means 聚类 —— 发现 Meta 阵容")
    print("=" * 60)

    df = cl_load()
    synergy_cols = [c for c in df.columns if c.startswith("syn_")]
    champion_cols = [c for c in df.columns if c.startswith("unit_")]

    df, X_scaled, kmeans = run_clustering(df, k=10)
    df = analyze_clusters(df, synergy_cols, champion_cols)

    plot_cluster_winrates(df)
    plot_cluster_pca(X_scaled, df, {})
    plot_cluster_size_distribution(df)
    print()


def step3_bis_items():
    """第3步：线性回归 BIS 装备推荐"""
    print("\n" + "=" * 60)
    print("  第3步：线性回归 —— 装备最优分析 (BIS)")
    print("=" * 60)

    df = bis_load()
    X, y = prepare_feature_matrix(df)
    model, coeffs = train_linear_regression(X, y)

    all_results = {}
    for champ_api in TARGET_CHAMPIONS:
        result = analyze_bis_for_champion(coeffs, champ_api)
        if result is not None:
            all_results[champ_api] = result

    for champ_api, champ_coeffs in all_results.items():
        save_name = champ_api.replace("TFT9_", "").lower()
        plot_bis_horizontal(champ_coeffs, champ_api, f"figures/bis_{save_name}.png")

    plot_bis_comparison(all_results)
    print()


def main():
    print("\n╔══════════════════════════════════════════════════╗")
    print("║     云顶之弈 (TFT) 机器学习分析系统             ║")
    print("║     实验任务5: Meta阵容聚类                      ║")
    print("║     实验任务7: 装备最优分配                      ║")
    print("╚══════════════════════════════════════════════════╝\n")

    step1_generate_data()
    step2_clustering()
    step3_bis_items()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║              全部任务完成！                     ║")
    print("║  图表输出: figures/ 目录                        ║")
    print("║  数据集:   data/tft_dump.parquet                 ║")
    print("╚══════════════════════════════════════════════════╝\n")


if __name__ == "__main__":
    main()
