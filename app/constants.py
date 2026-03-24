ERA_COLS = [
    "Star League (2571 - 2780)",
    "Early Succession War (2781 - 2900)",
    "Late Succession War - LosTech (2901 - 3019)",
    "Late Succession War - Renaissance (3020 - 3049)",
    "Clan Invasion (3050 - 3061)",
    "Civil War (3062 - 3067)",
    "Jihad (3068 - 3085)",
    "Early Republic (3086 - 3100)",
    "Late Republic (3101 - 3130)",
    "Dark Ages (3131 - 3150)",
    "ilClan (3151 - 9999)",
]

TYPE_HIERARCHY = [
    ("BattleMech", None),
    ("Combat Vehicle", None),
    ("Infantry", ["Battle Armor", "Conventional Infantry"]),
    ("Aerospace", ["Aerospace Fighter", "Conventional Fighter", "Jumpship", "Small Craft", "Support Satellite"]),
    ("IndustrialMech", None),
    ("Protomech", None),
    ("Building", None),
    ("Support Vehicle", None),
]
