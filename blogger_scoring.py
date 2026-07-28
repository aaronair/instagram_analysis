"""
Скоринг кандидатов-блогеров на соответствие портрету идеального блогера.

"""

IDEAL_BLOGGER_PROFILE = {
    "followers": {
        "min": 5_000,
        "max": 150_000,
        "weight": 0.15,
    },
    "median_er": {
        "min": 0.5,          # в процентах
        "preferred_min": 1.0,
        "weight": 0.25,
    },
    "er_stability_ratio": {
        # ER / median_ER не должен сильно превышать 1 —
        # иначе это разовый вирусный пост, а не стабильная вовлечённость
        "max_ratio": 3.0,
        "weight": 0.15,
    },
    "video_ratio": {
        "min": 0.7,
        "weight": 0.15,
    },
    "posts_per_month": {
        "min": 2,
        "max": 20,
        "weight": 0.10,
    },
    "bio_keywords": {
        "keywords": [
            "обзоры", "находки", "бьюти", "beauty",
            "дом", "стиль", "lifestyle", "fashion",
            "ugc", "распаковк", "образы",
        ],
        "min_matches": 1,
        "weight": 0.10,
    },
    "bio_has_location": {
        "weight": 0.05,
    },
    "bio_has_collab_contact": {
        # наличие "сотрудничество", "PR", "direct" и т.п.
        "keywords": ["сотрудничество", "pr", "direct", "директ"],
        "weight": 0.05,
    },
}



IDEAL_PROFILE_STRUCTURED = {
    "creator_type": [
        "lifestyle influencer",
        "ugc creator",
        "product reviewer"
    ],

    "niches": [
        "beauty",
        "fashion",
        "home",
        "marketplace finds",
        "family lifestyle"
    ],

    "content_formats": [
        "reels",
        "unboxing",
        "reviews",
        "tutorials",
        "daily vlog"
    ],

    "visual_style": {
        "warm": True,
        "natural_light": True,
        "home_environment": True,
        "non_studio": True
    },

    "communication_style": {
        "friendly": True,
        "informal": True,
        "personal": True,
        "emoji_usage": True
    },

    "audience": {
        "followers_min": 5000,
        "followers_max": 150000,
        "engagement_priority": "high_stable"
    },

    "commercial_signals": [
        "ugc",
        "pr",
        "collaboration",
        "direct",
        "brand_tags"
    ],

    "brands_fit": [
        "beauty",
        "fashion",
        "home",
        "marketplaces",
        "consumer_goods"
    ]
}

# Список городов для проверки геолокации в bio.
# Дополните своим списком регионов/городов, релевантных вашей аудитории.
KNOWN_CITIES = [
    "москва", "санкт-петербург", "спб", "сочи", "самара",
    "тула", "брянск", "вологда", "казань", "екатеринбург",
    "новосибирск", "краснодар", "ростов",
]


def score_candidate(candidate: dict, profile: dict = IDEAL_BLOGGER_PROFILE) -> float:
    """
    Считает скор кандидата от 0.0 до 1.0 на основе совпадения с идеальным профилем.

    Ожидаемые поля в candidate:
        - followers (int)
        - ER (float)
        - median_ER (float)
        - video_ratio (float, 0..1)
        - posts_per_month (float)
        - bio (str)
    """
    score = 0.0

    followers = candidate.get("followers", 0)
    if profile["followers"]["min"] <= followers <= profile["followers"]["max"]:
        score += profile["followers"]["weight"]

    median_er = candidate.get("median_ER", 0)
    if median_er >= profile["median_er"]["min"]:
        score += profile["median_er"]["weight"]

    er = candidate.get("ER", median_er)
    if median_er > 0 and (er / median_er) <= profile["er_stability_ratio"]["max_ratio"]:
        score += profile["er_stability_ratio"]["weight"]

    if candidate.get("video_ratio", 0) >= profile["video_ratio"]["min"]:
        score += profile["video_ratio"]["weight"]

    ppm = candidate.get("posts_per_month", 0)
    if profile["posts_per_month"]["min"] <= ppm <= profile["posts_per_month"]["max"]:
        score += profile["posts_per_month"]["weight"]

    bio = candidate.get("bio", "").lower()

    if any(kw in bio for kw in profile["bio_keywords"]["keywords"]):
        score += profile["bio_keywords"]["weight"]

    if any(city in bio for city in KNOWN_CITIES):
        score += profile["bio_has_location"]["weight"]

    if any(kw in bio for kw in profile["bio_has_collab_contact"]["keywords"]):
        score += profile["bio_has_collab_contact"]["weight"]

    return round(score, 3)  # от 0.0 до 1.0


if __name__ == "__main__":
    example_candidate = {
        "followers": 48_000,
        "ER": 1.2,
        "median_ER": 1.0,
        "video_ratio": 0.9,
        "posts_per_month": 8,
        "bio": "Юля | Дом • UGC • Стиль: Брянск. Сотрудничество: @pr.kotova.live",
    }

    result = score_candidate(example_candidate)
    print(f"Score кандидата: {result}")
