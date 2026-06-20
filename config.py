# TFT 云顶之弈数据定义
# 基于 Set 17 典型阵容结构

# ============================================================
# 棋子定义：{API名称: (中文名, 费用)}
# ============================================================
CHAMPIONS = {
    # 1费
    "TFT9_Illaoi": ("俄洛伊", 1),
    "TFT9_Cassiopeia": ("卡西奥佩娅", 1),
    "TFT9_ChoGath": ("科加斯", 1),
    "TFT9_Jhin": ("烬", 1),
    "TFT9_Maokai": ("茂凯", 1),
    "TFT9_Milio": ("米利欧", 1),
    "TFT9_Orianna": ("奥莉安娜", 1),
    "TFT9_Poppy": ("波比", 1),
    "TFT9_Renekton": ("雷克顿", 1),
    "TFT9_Samira": ("莎弥拉", 1),
    "TFT9_Taliyah": ("塔莉娅", 1),
    # 2费
    "TFT9_Ashe": ("艾希", 2),
    "TFT9_Galio": ("加里奥", 2),
    "TFT9_Jinx": ("金克丝", 2),
    "TFT9_Kassadin": ("卡萨丁", 2),
    "TFT9_Kled": ("克烈", 2),
    "TFT9_Naafiri": ("纳亚菲利", 2),
    "TFT9_Sett": ("瑟提", 2),
    "TFT9_Soraka": ("索拉卡", 2),
    "TFT9_Swain": ("斯维因", 2),
    "TFT9_Teemo": ("提莫", 2),
    "TFT9_Vi": ("蔚", 2),
    "TFT9_Warwick": ("沃里克", 2),
    "TFT9_Zed": ("劫", 2),
    # 3费
    "TFT9_Akshan": ("阿克尚", 3),
    "TFT9_Darius": ("德莱厄斯", 3),
    "TFT9_Ekko": ("艾克", 3),
    "TFT9_Gwen": ("格温", 3),
    "TFT9_Jayce": ("杰斯", 3),
    "TFT9_Karma": ("卡尔玛", 3),
    "TFT9_Katarina": ("卡特琳娜", 3),
    "TFT9_Lissandra": ("丽桑卓", 3),
    "TFT9_Lux": ("拉克丝", 3),
    "TFT9_RekSai": ("雷克塞", 3),
    "TFT9_Shen": ("慎", 3),
    "TFT9_Sona": ("娑娜", 3),
    "TFT9_Taric": ("塔里克", 3),
    "TFT9_VelKoz": ("维克兹", 3),
    # 4费
    "TFT9_Aphelios": ("厄斐琉斯", 4),
    "TFT9_Azir": ("阿兹尔", 4),
    "TFT9_Garen": ("盖伦", 4),
    "TFT9_JarvanIV": ("嘉文四世", 4),
    "TFT9_Kaisa": ("卡莎", 4),
    "TFT9_Lucian": ("卢锡安", 4),
    "TFT9_Nilah": ("尼菈", 4),
    "TFT9_Sejuani": ("瑟庄妮", 4),
    "TFT9_Shen": ("慎", 4),
    "TFT9_Urgot": ("厄加特", 4),
    "TFT9_Yasuo": ("亚索", 4),
    "TFT9_Zeri": ("泽丽", 4),
    # 5费
    "TFT9_Aatrox": ("亚托克斯", 5),
    "TFT9_Ahri": ("阿狸", 5),
    "TFT9_BelVeth": ("卑尔维斯", 5),
    "TFT9_Heimerdinger": ("黑默丁格", 5),
    "TFT9_Ksante": ("奎桑提", 5),
    "TFT9_Ryze": ("瑞兹", 5),
    "TFT9_Sion": ("赛恩", 5),
}

# ============================================================
# 羁绊定义：{API名称: 中文名}
# ============================================================
TRAITS = {
    "Set9_Demacia": "德玛西亚",
    "Set9_Noxus": "诺克萨斯",
    "Set9_Ionia": "艾欧尼亚",
    "Set9_Shurima": "恕瑞玛",
    "Set9_ShadowIsles": "暗影岛",
    "Set9_Freljord": "弗雷尔卓德",
    "Set9_Bilgewater": "比尔吉沃特",
    "Set9_Void": "虚空",
    "Set9_Yordle": "约德尔人",
    "Set9_Targon": "巨神峰",
    "Set9_Zaun": "祖安",
    "Set9_Piltover": "皮尔特沃夫",
    "Set9_BandleCity": "班德尔城",
    "Set9_Slayer": "杀手",
    "Set9_Sorcerer": "法师",
    "Set9_Bastion": "壁垒卫士",
    "Set9_Juggernaut": "主宰",
    "Set9_Challenger": "挑战者",
    "Set9_Invoker": "神谕者",
    "Set9_Gunner": "枪手",
    "Set9_Rogue": "潜行者",
    "Set9_Deadeye": "亡眼射手",
    "Set9_Strategist": "战略家",
    "Set9_Vanquisher": "征服者",
}

# ============================================================
# 装备定义：{API名称: 中文名}
# ============================================================
ITEMS = {
    "TFT_Item_Deathblade": "死亡之刃",
    "TFT_Item_GiantSlayer": "巨人杀手",
    "TFT_Item_GuinsoosRageblade": "鬼索的狂暴之刃",
    "TFT_Item_InfinityEdge": "无尽之刃",
    "TFT_Item_LastWhisper": "最后的轻语",
    "TFT_Item_RabadonsDeathcap": "灭世者的死亡之帽",
    "TFT_Item_JeweledGauntlet": "珠光护手",
    "TFT_Item_BlueBuff": "蓝霸符",
    "TFT_Item_SpearOfShojin": "朔极之矛",
    "TFT_Item_ArchangelsStaff": "大天使之杖",
    "TFT_Item_WarmogsArmor": "狂徒铠甲",
    "TFT_Item_BrambleVest": "棘刺背心",
    "TFT_Item_DragonsClaw": "巨龙之爪",
    "TFT_Item_GargoyleStoneplate": "石像鬼石板甲",
    "TFT_Item_Redemption": "救赎",
    "TFT_Item_SunfireCape": "日炎斗篷",
    "TFT_Item_ThiefsGloves": "窃贼手套",
    "TFT_Item_Quicksilver": "水银",
    "TFT_Item_Bloodthirster": "饮血剑",
    "TFT_Item_HandOfJustice": "正义之手",
    "TFT_Item_TitansResolve": "泰坦的坚决",
    "TFT_Item_EdgeOfNight": "夜之锋刃",
    "TFT_Item_RunaansHurricane": "卢安娜的飓风",
    "TFT_Item_StatikkShiv": "斯塔缇克电刃",
    "TFT_Item_IonicSpark": "离子火花",
    "TFT_Item_Morellonomicon": "莫雷洛秘典",
}

# ============================================================
# 已知 Meta 阵容模板（用于生成有"正确答案"的训练数据）
# 每套阵容有：核心羁绊（带等级要求）、核心棋子、核心装备
# ============================================================
META_COMPS = [
    {
        "name": "德玛西亚精英",
        "traits": {"Set9_Demacia": 3, "Set9_Slayer": 1, "Set9_Bastion": 1, "Set9_Juggernaut": 1},
        "core_units": ["TFT9_Garen", "TFT9_JarvanIV", "TFT9_Lucian", "TFT9_Sona", "TFT9_Poppy"],
        "core_items": {"TFT9_Garen": ["TFT_Item_WarmogsArmor", "TFT_Item_DragonsClaw", "TFT_Item_BrambleVest"]},
        "win_rate": 0.56,
    },
    {
        "name": "艾欧尼亚挑战者",
        "traits": {"Set9_Ionia": 3, "Set9_Challenger": 2, "Set9_Vanquisher": 1},
        "core_units": ["TFT9_Yasuo", "TFT9_Karma", "TFT9_Shen", "TFT9_Irelia", "TFT9_Warwick"],
        "core_items": {"TFT9_Yasuo": ["TFT_Item_Bloodthirster", "TFT_Item_TitansResolve", "TFT_Item_InfinityEdge"]},
        "win_rate": 0.53,
    },
    {
        "name": "恕瑞玛沙皇",
        "traits": {"Set9_Shurima": 3, "Set9_Strategist": 1, "Set9_Bastion": 1, "Set9_Juggernaut": 1},
        "core_units": ["TFT9_Azir", "TFT9_Nasus", "TFT9_JarvanIV", "TFT9_Taliyah", "TFT9_ChoGath"],
        "core_items": {"TFT9_Azir": ["TFT_Item_GuinsoosRageblade", "TFT_Item_GiantSlayer", "TFT_Item_JeweledGauntlet"]},
        "win_rate": 0.54,
    },
    {
        "name": "暗影岛佛耶戈",
        "traits": {"Set9_ShadowIsles": 3, "Set9_Rogue": 1, "Set9_Slayer": 1, "Set9_Bastion": 1},
        "core_units": ["TFT9_Gwen", "TFT9_Maokai", "TFT9_Kalista", "TFT9_Viego"],
        "core_items": {"TFT9_Gwen": ["TFT_Item_JeweledGauntlet", "TFT_Item_BlueBuff", "TFT_Item_GiantSlayer"]},
        "win_rate": 0.51,
    },
    {
        "name": "诺克萨斯主宰",
        "traits": {"Set9_Noxus": 3, "Set9_Juggernaut": 2, "Set9_Vanquisher": 1},
        "core_units": ["TFT9_Darius", "TFT9_Sion", "TFT9_Katarina", "TFT9_Swain", "TFT9_Kled"],
        "core_items": {"TFT9_Darius": ["TFT_Item_Bloodthirster", "TFT_Item_TitansResolve", "TFT_Item_InfinityEdge"]},
        "win_rate": 0.52,
    },
    {
        "name": "虚空法师",
        "traits": {"Set9_Void": 3, "Set9_Sorcerer": 2, "Set9_Bastion": 1},
        "core_units": ["TFT9_VelKoz", "TFT9_ChoGath", "TFT9_Kassadin", "TFT9_Malzahar"],
        "core_items": {"TFT9_VelKoz": ["TFT_Item_BlueBuff", "TFT_Item_JeweledGauntlet", "TFT_Item_RabadonsDeathcap"]},
        "win_rate": 0.50,
    },
    {
        "name": "比尔吉沃特枪手",
        "traits": {"Set9_Bilgewater": 3, "Set9_Gunner": 2, "Set9_Juggernaut": 1},
        "core_units": ["TFT9_Gangplank", "TFT9_MissFortune", "TFT9_Illaoi", "TFT9_Graves"],
        "core_items": {"TFT9_Gangplank": ["TFT_Item_InfinityEdge", "TFT_Item_LastWhisper", "TFT_Item_GuinsoosRageblade"]},
        "win_rate": 0.545,
    },
    {
        "name": "约德尔提莫",
        "traits": {"Set9_Yordle": 3, "Set9_Sorcerer": 2, "Set9_Strategist": 1},
        "core_units": ["TFT9_Teemo", "TFT9_Poppy", "TFT9_Tristana", "TFT9_Veigar"],
        "core_items": {"TFT9_Teemo": ["TFT_Item_BlueBuff", "TFT_Item_Morellonomicon", "TFT_Item_RabadonsDeathcap"]},
        "win_rate": 0.48,
    },
    {
        "name": "弗雷尔卓德塞恩",
        "traits": {"Set9_Freljord": 3, "Set9_Juggernaut": 2, "Set9_Bastion": 1},
        "core_units": ["TFT9_Sejuani", "TFT9_Sion", "TFT9_Ashe", "TFT9_Lissandra"],
        "core_items": {"TFT9_Sion": ["TFT_Item_WarmogsArmor", "TFT_Item_DragonsClaw", "TFT_Item_BrambleVest"]},
        "win_rate": 0.49,
    },
    {
        "name": "巨神峰神谕",
        "traits": {"Set9_Targon": 3, "Set9_Invoker": 2, "Set9_Bastion": 2},
        "core_units": ["TFT9_Taric", "TFT9_Soraka", "TFT9_Karma", "TFT9_Shen"],
        "core_items": {"TFT9_Karma": ["TFT_Item_JeweledGauntlet", "TFT_Item_BlueBuff", "TFT_Item_ArchangelsStaff"]},
        "win_rate": 0.47,
    },
]
