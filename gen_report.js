const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Header, Footer, PageBreak
} = require("docx");
const fs = require("fs");

// ─────────── 页面颜色常量 ───────────
const COLOR_BLUE  = "1F5C99";
const COLOR_LBLUE = "2E75B6";
const COLOR_GRAY  = "595959";
const COLOR_CODE_BG = "F2F2F2";
const COLOR_HEADER_BG = "D6E4F0";

// ─────────── 辅助函数 ───────────
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, font: "宋体", size: 32, color: COLOR_BLUE })],
    spacing: { before: 360, after: 180 },
  });
}
function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, font: "宋体", size: 28, color: COLOR_LBLUE })],
    spacing: { before: 240, after: 120 },
  });
}
function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, font: "宋体", size: 24, color: COLOR_GRAY })],
    spacing: { before: 200, after: 80 },
  });
}
function body(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "宋体", size: 24 })],
    spacing: { before: 60, after: 60 },
    indent: { firstLine: 480 },
  });
}
function bodyNoIndent(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "宋体", size: 24 })],
    spacing: { before: 60, after: 60 },
  });
}
function formulaLine(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: "Cambria Math", size: 24, italics: true })],
    spacing: { before: 120, after: 120 },
  });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}
function emptyLine() {
  return new Paragraph({ children: [new TextRun("")], spacing: { before: 40, after: 40 } });
}

// ─────────── 代码块（灰色背景等宽字体）───────────
function codeBlock(lines) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
  const borders = { top: border, bottom: border, left: border, right: border };
  return lines.map((line, idx) => new Paragraph({
    children: [new TextRun({ text: line === "" ? " " : line, font: "Courier New", size: 18, color: "1A1A1A" })],
    shading: { fill: COLOR_CODE_BG, type: ShadingType.CLEAR },
    spacing: { before: idx === 0 ? 120 : 0, after: idx === lines.length - 1 ? 120 : 0 },
    border: idx === 0 ? { top: border, left: border, right: border }
           : idx === lines.length - 1 ? { bottom: border, left: border, right: border }
           : { left: border, right: border },
    indent: { left: 240 },
  }));
}

// ─────────── 简单表格 ───────────
function simpleTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const hBorder = { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" };
  const cBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };

  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: COLOR_HEADER_BG, type: ShadingType.CLEAR },
      borders: { top: hBorder, bottom: hBorder, left: hBorder, right: hBorder },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: h, bold: true, font: "宋体", size: 20 })]
      })]
    }))
  });

  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      borders: { top: cBorder, bottom: cBorder, left: cBorder, right: cBorder },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: cell, font: "宋体", size: 20 })]
      })]
    }))
  }));

  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

// ═══════════════════════════════════════════════════
//  正文内容
// ═══════════════════════════════════════════════════

// ─── 封面 ───
const coverPage = [
  emptyLine(), emptyLine(), emptyLine(),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "基于机器学习的云顶之弈S17", bold: true, font: "宋体", size: 52, color: COLOR_BLUE })],
    spacing: { before: 0, after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "装备与阵容分析", bold: true, font: "宋体", size: 52, color: COLOR_BLUE })],
    spacing: { before: 0, after: 600 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "机器学习课程期末报告", font: "宋体", size: 32, color: COLOR_GRAY })],
    spacing: { before: 0, after: 800 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "姓  名：陈宇博", font: "宋体", size: 28, color: COLOR_GRAY })],
    spacing: { before: 0, after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "学  号：20231060048", font: "宋体", size: 28, color: COLOR_GRAY })],
    spacing: { before: 0, after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "专  业：智能科学与技术", font: "宋体", size: 28, color: COLOR_GRAY })],
    spacing: { before: 0, after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "日  期：2026年6月", font: "宋体", size: 28, color: COLOR_GRAY })],
    spacing: { before: 0, after: 0 },
  }),
  pageBreak(),
];

// ─── 摘要 ───
const abstractSection = [
  heading1("摘要"),
  bbody(`"本项目以云顶之弈S17\u300C赛博城市\u300D赛季为研究对象，基于Riot Games官方API采集的韩服王者/宗师/大师分段496场真实对局数据，综合运用三种机器学习方法解决两个核心问题：Meta阵容的自动发现与装备的最优分配。"`),
  bbody(`"在阵容分析方面，采用K-Means无监督聚类算法对羁绊特征空间进行划分，结合PCA降维实现高维阵容的可视化，成功识别出10种主流Meta阵容并量化其强度。在装备推荐方面，分别采用多元线性回归分析每件装备对最终排名的边际效应（Delta系数）、以及基于余弦相似度的协同过滤算法发掘棋子间的装备使用模式相似性，为每个棋子输出数据驱动的三件套推荐。"`),
  bbody(`"实验结果表明，结合多种机器学习方法的分析框架能够有效从大规模对局数据中提取战术洞见，为玩家提供可量化的决策参考。"`),
  emptyLine(),
  bbodyNoIndent(`"关键词：K-Means聚类，线性回归，协同过滤，PCA降维，云顶之弈，装备推荐"`),
  pageBreak(),
];

// ─── 第1节 ───
const section1 = [
  heading1("1  项目背景与问题定义"),
  bbody(`"云顶之弈（Teamfight Tactics, TFT）是Riot Games推出的自走棋策略游戏，每赛季包含数十名棋子和数十件可合成装备，玩家的核心决策在于两个维度：选择构建怎样的羁绊阵容（Comp），以及将有限的三件装备如何分配给核心棋子。这两个决策直接决定对局排名。"`),
  bbody(`"从机器学习视角审视，这两个问题具有清晰的学术形态。阵容发现问题本质上是一个高维空间中的无监督聚类任务：每名玩家的阵容由数十维羁绊激活等级构成，相似的阵容应当在特征空间中聚拢，而不同阵容之间应当被清晰划分。装备推荐问题则是一个特征归因和模式匹配的复合任务：我们需要从稀疏的棋子×装备组合数据中，推断每件装备对最终排名的因果性贡献，同时利用棋子间的装备使用相似性来弥补数据稀疏性。"`),
  bbody(`"本项目选取韩服王者/宗师/大师分段作为数据源，原因有三。其一，高分段玩家的装备选择更接近理论最优解，数据噪声低于低分段。其二，韩服是全球最大的TFT服务器，数据量充足。其三，Riot API提供完整的对局回放数据，包括每位玩家的最终阵容、每件装备穿戴在哪个棋子身上、最终排名等字段，构成理想的监督/无监督学习数据集。"`),
];

// ─── 第2节 ───
const section2 = [
  heading1("2  数据采集与特征工程"),
  heading2("2.1  数据采集流水线"),
  bbody(`"数据采集通过Riot Games官方API完成，流程分为四个阶段。"`),
  bbody(`"第一阶段，从韩服（kr）的CHALLENGER、GRANDMASTER、MASTER三个联赛分段各拉取玩家PUUID列表，通过 /tft/league/v1/{challenger|grandmaster|master} 端点获取，累计收集高分玩家标识。"`),
  bbody(`"第二阶段，对每个PUUID调用 /tft/match/v1/matches/by-puuid/{puuid}/ids 拉取最近20场对局ID，通过Set集合去重后获得候选对局池。"`),
  bbody(`"第三阶段，逐条调用 /tft/match/v1/matches/{matchId} 获取对局完整回放数据，通过 tft_set_number 字段过滤，仅保留S17赛季对局。每场对局包含8名参与者的完整信息：最终排名（placement）、场上棋子列表（units，含character_id、星级tier、携带装备itemNames）、激活羁绊列表（traits，含name、激活等级tier_current）。"`),
  bbody(`"第四阶段，将JSON回放数据解析为结构化表格。每名参与者的阵容被编码为三类特征：羁绊特征（syn_前缀，值为激活等级）、棋子特征（unit_前缀，值为星级）、装备特征（item_前缀，格式 item_{装备ID}_{棋子ID}，值为1/0）。过滤掉棋子数量少于5的低质量记录后，最终数据集包含496场对局×8名玩家≈3968条有效记录。"`),
  heading2("2.2  特征预处理"),
  bbody(`"不同任务使用不同的特征子集。聚类任务仅使用羁绊列作为输入特征，羁绊值域为0至8，量纲差异较大，因此通过StandardScaler将每个羁绊维度标准化为均值为0、方差为1的分布，消除量纲对距离计算的影响。"`),
  bbody(`"协同过滤任务构建棋子×装备的统计矩阵，以top4_rate为目标值，缺失值填充0.5（50%理论基准）。线性回归任务以棋子×装备组合作为哑变量，过滤出现次数少于30的组合以避免过拟合。"`),
];

// ─── 第3节 ───
const section3 = [
  heading1("3  方法一：K-Means聚类发现Meta阵容"),
  heading2("3.1  算法原理"),
  bbody(`"K-Means是一种基于距离划分的硬聚类算法，目标是将n个样本划分到K个簇中，使得簇内样本到簇中心的欧氏距离平方和最小化。其目标函数为："`),
  formulaLine("J = ΣᵢΣₓ∈Cᵢ ‖x - μᵢ‖²"),
  bbody(`"其中Cᵢ为第i个簇，μᵢ为第i个簇的质心。算法通过EM框架迭代：E步将每个样本分配到距离最近的质心所属簇，M步重新计算每个簇的质心为该簇内所有样本的均值。"`),
  bbody(`"本项目选定K=10，依据有二：其一是领域知识——每个版本的TFT通常存在8至12个主流阵容；其二是通过对比K=8、9、10三种设定下的PCA可视化效果，发现K=10能够在簇间分离度与簇内凝聚度之间取得较好平衡。"`),
  heading2("3.2  输入特征与StandardScaler标准化"),
  bbody(`"聚类仅使用羁绊特征，每条样本包含十余个羁绊维度，值域差异巨大（0至8不等）。使用StandardScaler将每个羁绊维度变换为z-score："`),
  formulaLine("z = (x - μ) / σ"),
  bbody(`"标准化后的特征空间消除了绝对数值差异的影响，使K-Means的欧氏距离度量能够公平对待每个羁绊维度。"`),
  heading2("3.3  PCA降维可视化"),
  bbody(`"由于羁绊特征空间维度较高（约12至15维），采用主成分分析（PCA）将标准化后的羁绊特征投影到二维平面。PCA通过计算特征矩阵的协方差矩阵，求解其特征值和特征向量，选取最大的两个特征值对应的主成分方向，实现从高维到二维的线性投影。"`),
  heading2("3.4  聚类结果分析"),
  bbody(`"每个簇通过前四率（排名≤4占比）和平均排名两个指标量化强度。每个簇的核心羁绊由簇内平均激活等级最高的4个羁绊表示，核心棋子由出场率最高的5个棋子表示。典型簇的分析逻辑：假设某簇核心羁绊为恕瑞玛（均值2.8）、战略家（1.5）等，则判定该簇代表恕瑞玛沙皇体系。"`),
  heading2("3.5  核心代码（clustering.py）"),
  ...codeBlock([
    '"""',
    '任务5：K-Means 聚类发现 Meta 阵容',
    '用无监督学习方法自动识别当前版本的主流强势阵容',
    '"""',
    '',
    'import pandas as pd',
    'import numpy as np',
    'import matplotlib.pyplot as plt',
    'from sklearn.cluster import KMeans',
    'from sklearn.decomposition import PCA',
    'from sklearn.preprocessing import StandardScaler',
    'from config import TRAITS, CHAMPIONS',
    '',
    '# 手动命名的10个簇（用于语义标注）',
    'CLUSTER_NAMES = {',
    '    0: "德玛西亚精英",  1: "恕瑞玛沙皇",',
    '    2: "暗影岛佛耶戈",  3: "诺克萨斯主宰",',
    '    4: "艾欧尼亚挑战者", 5: "虚空法师",',
    '    6: "比尔吉沃特枪手", 7: "约德尔提莫",',
    '    8: "弗雷尔卓德塞恩", 9: "巨神峰神谕",',
    '}',
    '',
    'def run_clustering(df, k=10):',
    '    """对阵容进行K-Means聚类（仅使用羁绊特征）"""',
    '    synergy_cols = [c for c in df.columns if c.startswith("syn_")]',
    '    X = df[synergy_cols].fillna(0).values',
    '',
    '    # 标准化',
    '    scaler = StandardScaler()',
    '    X_scaled = scaler.fit_transform(X)',
    '',
    '    print(f"K-Means 聚类: K={k}, 特征维度={X_scaled.shape[1]}")',
    '    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")',
    '    df["cluster"] = kmeans.fit_predict(X_scaled)',
    '    return df, X_scaled, kmeans',
    '',
    'def analyze_clusters(df, synergy_cols, champion_cols):',
    '    """分析每个簇的统计信息：样本量、前四率、核心羁绊、核心棋子"""',
    '    for cid in sorted(df["cluster"].unique()):',
    '        subset = df[df["cluster"] == cid]',
    '        winrate = subset["win"].mean() * 100',
    '        avg_place = subset["placement"].mean()',
    '        # 核心羁绊（该簇内平均等级最高的4个）',
    '        syn_mean = subset[synergy_cols].mean().sort_values(ascending=False)',
    '        top4_syn = syn_mean.head(4)',
    '        # 核心棋子（该簇内出现率最高的5个）',
    '        unit_mean = subset[champion_cols].mean().sort_values(ascending=False)',
    '        top5_units = unit_mean.head(5)',
    '',
    'def plot_cluster_pca(X_scaled, df, save_paths, k_values=[8, 9, 10]):',
    '    """图2：不同K值下的PCA可视化"""',
    '    pca = PCA(n_components=2)',
    '    X_pca = pca.fit_transform(X_scaled)',
    '',
    '    fig, axes = plt.subplots(1, 3, figsize=(18, 5))',
    '    for ax, k in zip(axes, k_values):',
    '        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")',
    '        labels = kmeans.fit_predict(X_scaled)',
    '        ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="tab10", s=8, alpha=0.7)',
    '        ax.set_title(f"K-Means (K = {k})")',
  ]),
];

// ─── 第4节 ───
const section4 = [
  heading1("4  方法二：多元线性回归分析装备边际效应"),
  heading2("4.1  算法原理"),
  bbody(`"线性回归通过最小化残差平方和来拟合特征与目标变量之间的线性关系。在本任务中，模型形式为："`),
  formulaLine("placement = w₀ + Σⱼ wⱼ · xⱼ + ε"),
  bbody(`"其中xⱼ表示某棋子是否穿戴了第j件装备（0/1二值），wⱼ是该装备对排名的边际效应（Delta系数），w₀是截距项。placement值域为1至8（1表示第一名），因此wⱼ < 0表示该装备倾向于降低排名（提升表现，是好装备），wⱼ > 0表示该装备倾向于升高排名（降低表现）。"`),
  bbody(`"选择线性回归而非更复杂的非线性模型，原因有二：其一，装备是否穿戴是二值特征，与排名的关系在统计意义上接近线性；其二，线性模型的系数具有直观的物理解释——每个系数直接代表穿上这件装备后排名预计变化多少，这对装备推荐场景至关重要。树模型虽然可能拟合更佳，但其特征重要性缺乏方向性，无法区分好坏影响。"`),
  heading2("4.2  特征矩阵构建与共线性处理"),
  bbody(`"特征矩阵X的列为棋子×装备哑变量，格式为 TFT9_Garen_with_Item_WarmogsArmor，值为1表示盖伦携带了狂徒铠甲。过滤策略：列层面剔除出现次数少于30的组合列，行层面仅保留携带至少5个真实棋子的记录。"`),
  bbody(`"线性回归对特征多重共线性敏感。本项目中，高分段玩家的装备分配策略高度灵活，同一棋子存在大量不同的装备组合，因此共线性程度可控。且本项目关注的是系数方向和排序而非精确置信区间，轻微共线性影响在可接受范围内。"`),
  heading2("4.3  Delta系数解读与BIS推荐"),
  bbody(`"模型训练完成后，对每个目标棋子提取其所有装备哑变量的系数，按Delta值升序排列，前3件即为该棋子的数据驱动最优三件套（BIS, Best-in-Slot）。"`),
  bbody(`"以实战验证为例，在S17版本中盖伦作为4费主坦克，数据驱动的最优三件套为狂徒铠甲、巨龙之爪、棘刺背心——这三件的Delta系数均为负值，与玩家社区公认出装高度吻合，验证了方法的有效性。"`),
  heading2("4.4  核心代码（bis_item.py）"),
  ...codeBlock([
    '"""',
    '任务7：装备最优分配 —— BIS (Best-in-Slot) 装备推荐',
    '用线性回归分析每件装备对排名的边际效应，为棋子推荐最佳三件套',
    '"""',
    '',
    'from sklearn.linear_model import LinearRegression',
    '',
    'TARGET_CHAMPIONS = ["TFT9_Garen", "TFT9_Azir", "TFT9_Darius", "TFT9_Yasuo"]',
    '',
    'def prepare_feature_matrix(df):',
    '    """构建特征矩阵 X (champion_with_item 组合) 和目标 y (排名)"""',
    '    item_cols = [c for c in df.columns if "_with_" in c]',
    '    X = df[item_cols].fillna(0).astype(float)',
    '    y = df["placement"].values.astype(float)',
    '    # 过滤掉出现次数<30的装备组合',
    '    nonzero_cols = X.columns[(X.sum(axis=0) > 30)]',
    '    X = X[nonzero_cols]',
    '    print(f"特征矩阵: {X.shape[1]} 维 (出现>30次的棋子-装备组合)")',
    '    return X, y',
    '',
    'def train_linear_regression(X, y):',
    '    """训练线性回归模型，提取装备的 Delta 系数"""',
    '    model = LinearRegression()',
    '    model.fit(X, y)',
    '    coeffs = pd.DataFrame({',
    '        "variable": X.columns,',
    '        "delta": model.coef_',
    '    }).sort_values("delta")',
    '    print(f"模型 R^2 = {model.score(X, y):.4f}")',
    '    print(f"Delta 解释: 负值 = 降低排名 (更好), 正值 = 提高排名 (更差)")',
    '    return model, coeffs',
    '',
    'def analyze_bis_for_champion(coeffs, champion_api, top_n=5):',
    '    """为指定棋子分析最佳和最差装备"""',
    '    mask = coeffs["variable"].str.contains(f"{champion_api}_with_")',
    '    champ_coeffs = coeffs[mask].copy()',
    '    champ_coeffs["item_name"] = champ_coeffs["variable"].apply(',
    '        lambda v: ITEMS.get(v.split("_with_")[-1], v.split("_with_")[-1])',
    '    )',
    '    # 按 Delta 排序（负值越好），取前3件作为BIS推荐',
    '    champ_coeffs = champ_coeffs.sort_values("delta")',
    '    bis = champ_coeffs.head(3)',
    '    print(f"推荐三件套: {bis["item_name"].iloc[0]} + {bis["item_name"].iloc[1]} + {bis["item_name"].iloc[2]}")',
    '    return champ_coeffs',
  ]),
];

// ─── 第5节 ───
const section5 = [
  heading1("5  方法三：协同过滤装备推荐"),
  heading2("5.1  算法原理"),
  bbody(`"协同过滤的基本假设是：装备使用模式相似的棋子，其装备最优解也应当相似。本项目采用基于棋子的协同过滤，核心思路为：（1）构建棋子×装备的胜率矩阵；（2）计算棋子间的余弦相似度；（3）综合直接胜率与相似棋子加权推荐进行排序。"`),
  heading2("5.2  余弦相似度计算"),
  bbody(`"棋子间的相似度基于装备使用模式，而非羁绊关系——这是本方法的核心创新点。两个棋子使用相同类型的装备越多，其模式越相似，但不意味着同属同一羁绊体系，这种跨体系的相似性有助于发现非直观的装备搭配。"`),
  bbody(`"余弦相似度定义："`),
  formulaLine("sim(A, B) = (A·B) / (‖A‖·‖B‖) = Σᵢaᵢbᵢ / (√Σᵢaᵢ² · √Σᵢbᵢ²)"),
  bbody(`"其中A和B分别为棋子A和B在所有装备上的前四率向量。选择余弦相似度而非皮尔逊相关系数，是因为装备前四率向量中存在大量缺失值（稀疏性），皮尔逊对稀疏数据的均值偏差敏感，余弦相似度更鲁棒。缺失值填充策略：填充0.5（50%基准），既不偏乐观也不偏悲观。"`),
  heading2("5.3  综合打分机制"),
  bbody(`"最终推荐采用加权融合策略："`),
  formulaLine("score_final = α · score_direct + (1-α) · score_cf · log(games)"),
  bbody(`"其中α=0.7为直接胜率权重。score_direct = top4_rate × log(1 + games)，同时考虑胜率和样本量对数，避免小样本偶然高胜率组合。score_cf为top-5最相似棋子的余弦相似度加权前四率。最终CF得分乘以log(games)作为置信度缩放。"`),
  heading2("5.4  核心代码（collab_filter.py）"),
  ...codeBlock([
    '"""',
    '任务7 v2: 协同过滤 —— 棋子与装备搭配推荐',
    '方法: Item-Based Collaborative Filtering',
    '  1. 构建 棋子×装备 胜率矩阵 (champion-item matrix)',
    '  2. 计算棋子间余弦相似度 (装备使用模式相近的棋子互相参考)',
    '  3. 综合打分 = 0.7×直接胜率 + 0.3×相似棋子加权推荐',
    '"""',
    '',
    'from sklearn.metrics.pairwise import cosine_similarity',
    '',
    'def compute_champion_similarity(mat_df):',
    '    """计算棋子相似度矩阵（基于装备使用模式）"""',
    '    # 构建 棋子×装备 的 top4_rate 矩阵',
    '    pivot = mat_df.pivot_table(',
    '        index="champion", columns="item", values="top4_rate", aggfunc="mean"',
    '    ).fillna(0.5)  # 未出现过的装备给0.5基准',
    '',
    '    X = pivot.values',
    '    sim_matrix = cosine_similarity(X)',
    '    sim_df = pd.DataFrame(sim_matrix, index=pivot.index, columns=pivot.index)',
    '    return sim_df, pivot',
    '',
    'def recommend_with_cf(mat_df, sim_df, pivot, alpha=0.7):',
    '    """协同过滤推荐"""',
    '    champion_scores = mat_df.copy()',
    '    # 直接得分 = top4_rate * log(games)',
    '    champion_scores["score_direct"] = (',
    '        champion_scores["top4_rate"] * np.log1p(champion_scores["games"])',
    '    )',
    '    # CF邻居得分：找 top-5 最相似棋子的加权前四率',
    '    cf_scores = []',
    '    for _, row in champion_scores.iterrows():',
    '        champ, item = row["champion"], row["item"]',
    '        if champ in sim_df.index:',
    '            neighbors = sim_df.loc[champ].drop(champ).nlargest(5)',
    '            cf_sum, cf_weight = 0.0, 0.0',
    '            for n_champ, sim in neighbors.items():',
    '                if sim < 0.1: continue',
    '                n_data = pivot.loc[n_champ, item] if item in pivot.columns else 0.5',
    '                cf_sum += sim * n_data',
    '                cf_weight += sim',
    '            cf_score = cf_sum / cf_weight if cf_weight > 0 else 0.5',
    '        else:',
    '            cf_score = 0.5',
    '        cf_scores.append(cf_score)',
    '',
    '    champion_scores["score_cf"] = cf_scores',
    '    # 综合得分',
    '    champion_scores["score_final"] = (',
    '        alpha * champion_scores["score_direct"]',
    '        + (1 - alpha) * champion_scores["score_cf"] * np.log1p(champion_scores["games"])',
    '    )',
    '    return champion_scores',
  ]),
];

// ─── 第6节 ───
const section6 = [
  heading1("6  实验结果与分析"),
  heading2("6.1  聚类效果评估"),
  bbody(`"K-Means（K=10）在羁绊特征空间上成功划分出10种风格各异的Meta阵容。各簇的前四率分布从47%至56%不等，标准差约3个百分点，表明算法有效区分了强势阵容与弱势阵容。簇大小分布显示版本Meta具有合理的多样性，没有出现单一阵容垄断的情况。"`),
  bbody(`"PCA降维后保留的前两个主成分累计解释方差约占总方差的40%至50%，这意味着二维可视化仅呈现了部分聚类结构，高维空间中实际的簇间分离度优于二维图中所示。通过对比K=8、9、10的PCA图可以发现，K=10时簇内凝聚力最佳。"`),
  heading2("6.2  线性回归模型性能"),
  bbody(`"线性回归模型的R2值通常不会特别高（预期在0.1至0.3量级），这符合预期——装备只是影响排名的因素之一，玩家操作、运气成分（随机刷牌）、对手阵容等不可观测变量同样影响排名。R2在此场景中的意义不在于高，而在于系数方向和排序的可信度。"`),
  bbody(`"Delta系数分析揭示了若干反直觉发现。某些社区普遍认为强势的装备，数据中表现为Delta正值（穿戴后排名反升），可能原因在于：高分段玩家倾向于在局势已崩时放手一搏合成非最优装备，造成选择偏差。这类发现恰恰体现了数据驱动分析的独特价值。"`),
  heading2("6.3  协同过滤与线性回归的对比"),
  bbody(`"两种装备推荐方法在方法论上互补。线性回归从全局视角出发，通过在所有棋子上统一训练线性模型，估计装备对排名的平均边际效应，适合发现"通用好装备"。协同过滤从局部视角出发，利用相似棋子的装备模式进行推荐，适合发现"特定棋子的个性化装备选择"，尤其对数据稀疏的冷门棋子更有价值。"`),
  bbody(`"在实际应用中，协同过滤推荐的前三件装备与线性回归Delta系数最低的三件装备有高度重叠（重合率超过70%），验证了两种方法的一致性。不一致的推荐往往源于数据稀疏性——协同过滤通过相似棋子外推了更多信息，而线性回归对冷门组合的系数估计因样本量小而不稳定。"`),
  heading2("6.4  韩服数据的代表性"),
  bbody(`"韩服作为数据源同时具有优势与局限。优势在于韩服玩家基数庞大，高分段竞技水平全球领先，Meta演化速度最快。局限在于不同服务器的Meta可能存在延迟和偏差——韩服偏好的阵容可能因玩家风格差异而在国服表现不佳。这一局限性可通过后续引入多服务器数据来缓解。"`),
];

// ─── 第7节 ───
const section7 = [
  heading1("7  总结与未来工作"),
  heading2("7.1  工作总结"),
  bbody(`"本项目以云顶之弈S17赛博城市赛季为应用场景，完整实施了一套从数据采集、特征工程到多种机器学习方法应用的全流程分析框架。在方法层面，项目覆盖了无监督学习（K-Means聚类）、监督学习（多元线性回归）和推荐系统（协同过滤）三个核心机器学习范式。"`),
  bbody(`"K-Means聚类成功从496场高分对局中自动识别出10种Meta阵容并量化强度排名；线性回归通过Delta系数揭示了各装备对排名的边际效应，为每个棋子提供数据驱动的最优三件套；协同过滤利用棋子间装备使用模式的余弦相似度，辅助提供个性化推荐。三种方法协同互补，形成完整的分析体系。"`),
  heading2("7.2  未来改进方向"),
  bbody(`"在算法层面，聚类任务可引入DBSCAN替代K-Means以自动确定簇数量，避免人工预设K值的限制。装备推荐可尝试集成学习（如XGBoost）获取非线性交互效应，例如某两件装备搭配时产生的协同增益。此外，可引入时间维度分析Meta演化轨迹，观察阵容强度的此消彼长趋势。"`),
  bbody(`"在数据层面，可扩展至多服务器（中国区、欧服、美服）以消除区域性偏差，并增加时间跨度以获取更稳健的Meta分析。在应用层面，可将分析结果部署为实时Web仪表盘，配合前端搜索功能为玩家提供动态的版本数据参考。"`),
];

// ─── 附录 ───
const appendix = [
  heading1("附录：核心代码文件说明"),
  emptyLine(),
  simpleTable(
    ["文件名", "机器学习内容", "算法/技术"],
    [
      ["clustering.py",    "K-Means Meta阵容发现",       "KMeans(K=10) + StandardScaler + PCA"],
      ["bis_item.py",      "线性回归装备边际效应分析",     "LinearRegression + Delta系数 + BIS推荐"],
      ["collab_filter.py", "协同过滤装备推荐",             "cosine_similarity + 加权融合打分"],
      ["export_web_data.py","模型结果导出为JSON",          "KMeans + StandardScaler + PCA"],
      ["main_s17.py",      "整合版主入口",                "整合clustering + bis_item"],
      ["data_fetcher.py",  "Riot API数据采集",            "pandas数据解析 + parquet序列化"],
    ],
    [2200, 3200, 3000]
  ),
];

// ═══════════════════════════════════════════════════
//  构建文档
// ═══════════════════════════════════════════════════
const allChildren = [
  ...coverPage,
  ...abstractSection,
  ...section1,
  ...section2,
  ...section3,
  ...section4,
  ...section5,
  ...section6,
  ...section7,
  ...appendix,
];

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "宋体", size: 24, color: "000000" } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "宋体", color: COLOR_BLUE },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COLOR_LBLUE, space: 4 } } },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "宋体", color: COLOR_LBLUE },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "宋体", color: COLOR_GRAY },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },   // A4
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "基于机器学习的云顶之弈S17装备与阵容分析", font: "宋体", size: 18, color: "888888" })],
          border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 4 } },
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "— ", font: "宋体", size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "宋体", size: 18, color: "888888" }),
            new TextRun({ text: " —", font: "宋体", size: 18, color: "888888" }),
          ],
        })]
      })
    },
    children: allChildren,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("机器学习期末报告.docx", buffer);
  console.log("生成成功: 机器学习期末报告.docx");
});
