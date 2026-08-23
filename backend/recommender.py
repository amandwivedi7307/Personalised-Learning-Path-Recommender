import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

import ast
import json
import re
import urllib.parse


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("courses_dataset_final.csv")

# Convert prerequisites from string to Python list
df["prerequisites"] = df["prerequisites"].apply(
    lambda x: ast.literal_eval(x)
    if isinstance(x, str)
    else x
)

# Make sure skills are strings
df["skills"] = df["skills"].fillna("").astype(str)

print("Dataset shape:", df.shape)
print(df.head())


# ============================================================
# 2. TF-IDF MODEL
# ============================================================

# Combine course name + skills
df["search_text"] = (
    df["course_name"].fillna("").astype(str)
    + " "
    + df["skills"].fillna("").astype(str)
)

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

course_vectors = vectorizer.fit_transform(
    df["search_text"]
)

print(
    "TF-IDF matrix shape:",
    course_vectors.shape
)

print(
    "TF-IDF matrix shape:",
    course_vectors.shape
)


# ============================================================
# 3. K-MEANS CLUSTERING
# ============================================================

NUM_CLUSTERS = min(11, len(df))

kmeans = KMeans(
    n_clusters=NUM_CLUSTERS,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(
    course_vectors
)

print(
    "Clusters created:",
    df["cluster"].nunique()
)


# ============================================================
# 4. SKILL LEVEL MAP
# ============================================================

SKILL_LEVEL_MAP = {

    "None": 0,

    "Basic": 1,
    "Beginner": 1,

    "Medium": 2,
    "Intermediate": 2,

    "High": 3,
    "Advanced": 3
}


# ============================================================
# 5. CLEAN TEXT
# ============================================================

def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9+#.\- ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 6. EXTRACT SKILLS FROM DATASET
# ============================================================

def extract_skills(skill_text):

    if not isinstance(skill_text, str):
        return []

    # Handle comma, |, ; and /
    parts = re.split(
        r"[,|;/]",
        skill_text
    )

    skills = []

    for skill in parts:

        skill = skill.strip()

        if skill:
            skills.append(skill)

    return skills


# ============================================================
# 7. FIND RELEVANT SKILLS FOR USER GOAL
# ============================================================

def get_relevant_skills(
    user_goal,
    top_n=6
):

    user_goal = clean_text(
        user_goal
    )

    if not user_goal:
        return []


    # --------------------------------------------------------
    # Convert user goal into TF-IDF vector
    # --------------------------------------------------------

    goal_vector = vectorizer.transform(
        [user_goal]
    )


    # --------------------------------------------------------
    # Compare goal with every course
    # --------------------------------------------------------

    similarities = cosine_similarity(
        goal_vector,
        course_vectors
    ).flatten()


    # --------------------------------------------------------
    # Get top relevant courses
    # --------------------------------------------------------

    top_indices = similarities.argsort()[
        ::-1
    ][:30]


    # --------------------------------------------------------
    # Collect skills from relevant courses
    # --------------------------------------------------------

    skill_scores = {}

    for idx in top_indices:

        similarity = similarities[idx]

        # Ignore completely unrelated courses
        if similarity <= 0:
            continue


        course_skills = extract_skills(
            df.iloc[idx]["skills"]
        )


        for skill in course_skills:

            clean_skill = skill.strip()

            if not clean_skill:
                continue


            # Add similarity score
            skill_scores[clean_skill] = (
                skill_scores.get(
                    clean_skill,
                    0
                )
                + similarity
            )


    # --------------------------------------------------------
    # Rank skills according to relevance
    # --------------------------------------------------------

    ranked_skills = sorted(
        skill_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


    # --------------------------------------------------------
    # Return top relevant skills
    # --------------------------------------------------------

    return [
        skill
        for skill, score in ranked_skills[:top_n]
    ]


# ============================================================
# 8. SKILL GAP ANALYSIS
# ============================================================

def analyze_skill_gap(
    user_skills,
    required_skills
):

    gap_report = {}

    for skill in required_skills:

        current_level = SKILL_LEVEL_MAP.get(
            user_skills.get(
                skill,
                "None"
            ),
            0
        )

        gap_score = 3 - current_level


        if gap_score >= 2:
            priority = "High"

        elif gap_score == 1:
            priority = "Medium"

        else:
            priority = "Low"


        gap_report[skill] = {

            "current_level":
                user_skills.get(
                    skill,
                    "None"
                ),

            "gap_score":
                gap_score,

            "priority":
                priority
        }


    return gap_report


# ============================================================
# 9. YOUTUBE SEARCH LINK
# ============================================================

def generate_youtube_link(
    course_name: str
) -> str:

    clean_name = re.sub(
        r"\([^)]*\)",
        "",
        course_name
    ).strip()

    query = (
        clean_name
        + " tutorial"
    )

    return (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )


# ============================================================
# 10. COURSE SEARCH LINK
# ============================================================

def generate_course_search_link(
    course_name: str,
    provider: str = None
) -> str:

    clean_name = re.sub(
        r"\([^)]*\)",
        "",
        course_name
    ).strip()


    if provider:

        query = (
            f"{clean_name} "
            f"{provider} course"
        )

    else:

        query = (
            f"{clean_name} "
            f"online course"
        )


    return (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )


# ============================================================
# 11. COURSE RECOMMENDATION
# ============================================================

def recommend_courses(
    user_interests: str,
    top_n: int = 5
):

    user_interests = clean_text(
        user_interests
    )


    if not user_interests:
        return []


    # --------------------------------------------------------
    # Convert user goal to vector
    # --------------------------------------------------------

    user_vector = vectorizer.transform(
        [user_interests]
    )


    # --------------------------------------------------------
    # Predict relevant cluster
    # --------------------------------------------------------

    predicted_cluster = kmeans.predict(
        user_vector
    )[0]


    # --------------------------------------------------------
    # Select courses from cluster
    # --------------------------------------------------------

    cluster_df = df[
        df["cluster"] == predicted_cluster
    ].copy()


    # --------------------------------------------------------
    # Calculate similarity
    # --------------------------------------------------------

    cluster_vectors = vectorizer.transform(
        cluster_df["search_text"]
    )


    similarity_scores = cosine_similarity(
        user_vector,
        cluster_vectors
    ).flatten()


    cluster_df[
        "similarity"
    ] = similarity_scores


    # --------------------------------------------------------
    # Rank by similarity + rating
    # --------------------------------------------------------

    ranked = cluster_df.sort_values(
        by=[
            "similarity",
            "rating"
        ],
        ascending=[
            False,
            False
        ]
    ).head(top_n)


    # --------------------------------------------------------
    # Convert to JSON records
    # --------------------------------------------------------

    results = ranked[
        [
            "course_id",
            "course_name",
            "level",
            "rating",
            "similarity",
            "cluster"
        ]
    ].to_dict(
        orient="records"
    )


    # --------------------------------------------------------
    # Add useful links
    # --------------------------------------------------------

    for course in results:

        course["youtube_link"] = (
            generate_youtube_link(
                course["course_name"]
            )
        )

        course[
            "course_search_link"
        ] = generate_course_search_link(
            course["course_name"]
        )


    return results


# ============================================================
# 12. BUILD LEARNING ROADMAP
# ============================================================

def build_roadmap(
    course_ids
):

    course_map = df.set_index(
        "course_id"
    ).to_dict(
        orient="index"
    )


    visited = []

    result = []


    def visit(cid):

        if cid in visited:
            return

        if cid not in course_map:
            return


        visited.append(cid)


        prerequisites = course_map[
            cid
        ].get(
            "prerequisites",
            []
        )


        if not isinstance(
            prerequisites,
            list
        ):

            prerequisites = []


        for prereq in prerequisites:

            visit(prereq)


        result.append(cid)


    # Visit recommended courses
    for cid in course_ids:

        visit(cid)


    # --------------------------------------------------------
    # Convert roadmap into readable format
    # --------------------------------------------------------

    roadmap = []


    for i, cid in enumerate(
        result,
        start=1
    ):

        course = course_map[cid]


        roadmap.append({

            "step": i,

            "course_id": cid,

            "course_name":
                course["course_name"],

            "level":
                course["level"]
        })


    return roadmap


# ============================================================
# 13. MODULE UNLOCK CHECK
# ============================================================

def check_unlock_next(
    current_score,
    threshold=75.0
):

    unlocked = (
        current_score >= threshold
    )


    return {

        "score":
            current_score,

        "threshold":
            threshold,

        "unlocked_next_module":
            unlocked,

        "message":
            (
                "Great job! Next module unlocked."
                if unlocked
                else
                f"Score {current_score}% is below "
                f"{threshold}%. Revise and retry."
            )
    }


# ============================================================
# 14. COMPLETE LEARNING PATH
# ============================================================

def generate_learning_path(
    user_profile
):

    # --------------------------------------------------------
    # User information
    # --------------------------------------------------------

    name = user_profile.get(
        "name",
        "Learner"
    )

    goal = user_profile.get(
        "goal",
        ""
    )

    current_skills = user_profile.get(
        "current_skills",
        {}
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # Required skills are automatically found from
    # the dataset based on user's goal.
    # --------------------------------------------------------

    required_skills = get_relevant_skills(
        goal,
        top_n=6
    )


    # --------------------------------------------------------
    # If no relevant skills found
    # --------------------------------------------------------

    if not required_skills:

        return {

            "user": name,

            "goal": goal,

            "skill_gap_analysis": {},

            "recommended_courses": [],

            "learning_roadmap": [],

            "message":
                "No relevant skills found for this goal."
        }


    # --------------------------------------------------------
    # Skill Gap Analysis
    # --------------------------------------------------------

    skill_gap = analyze_skill_gap(
        current_skills,
        required_skills
    )


    # --------------------------------------------------------
    # Recommend relevant courses
    # --------------------------------------------------------

    recommended = recommend_courses(
        goal,
        top_n=5
    )


    # --------------------------------------------------------
    # Build roadmap
    # --------------------------------------------------------

    course_ids = [
        course["course_id"]
        for course in recommended
    ]


    roadmap = build_roadmap(
        course_ids
    )


    # --------------------------------------------------------
    # Calculate readiness
    # --------------------------------------------------------

    total_score = 0

    if required_skills:

        for skill in required_skills:

            current_level = SKILL_LEVEL_MAP.get(
                current_skills.get(
                    skill,
                    "None"
                ),
                0
            )

            total_score += (
                current_level / 3
            )


        current_readiness = round(
            (
                total_score
                / len(required_skills)
            ) * 100
        )

    else:

        current_readiness = 0


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "user": name,

        "goal": goal,

        "required_skills":
            required_skills,

        "current_readiness":
            current_readiness,

        "skill_gap_analysis":
            skill_gap,

        "recommended_courses":
            recommended,

        "learning_roadmap":
            roadmap
    }


# ============================================================
# 15. LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample_user = {

        "name": "Aman",

        "goal":
            "I want to become an App Developer",

        "current_skills": {}

    }


    output = generate_learning_path(
        sample_user
    )


    print(
        json.dumps(
            output,
            indent=2,
            default=str
        )
    )