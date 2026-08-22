


import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import ast
import json
import re
import urllib.parse




df = pd.read_csv("courses_dataset_final.csv")
df["prerequisites"] = df["prerequisites"].apply(ast.literal_eval)
print(df.shape)
df.head(10)



vectorizer = TfidfVectorizer()
course_vectors = vectorizer.fit_transform(df["skills"])
print("TF-IDF matrix shape:", course_vectors.shape)



NUM_CLUSTERS = 11
kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(course_vectors)

print(df["cluster"].value_counts())




SKILL_LEVEL_MAP = {"None": 0, "Basic": 1, "Beginner": 1, "Medium": 2, "Intermediate": 2, "High": 3, "Advanced": 3}

def analyze_skill_gap(user_skills, required_skills):
    gap_report = {}
    for skill in required_skills:
        current_level = SKILL_LEVEL_MAP.get(user_skills.get(skill, "None"), 0)
        gap_score = 3 - current_level
        gap_report[skill] = {
            "current_level": user_skills.get(skill, "None"),
            "gap_score": gap_score,
            "priority": "High" if gap_score >= 2 else ("Medium" if gap_score == 1 else "Low")
        }
    return gap_report





def generate_youtube_link(course_name: str) -> str:
    """Builds a real YouTube search URL for a course name (no API key needed)."""
    clean_name = re.sub(r"\([^)]*\)", "", course_name).strip()
    query = clean_name + " tutorial"
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)


def generate_course_search_link(course_name: str, provider: str = None) -> str:
    """Builds a Google search URL to help the user find the course online."""
    clean_name = re.sub(r"\([^)]*\)", "", course_name).strip()
    query = f"{clean_name} {provider} course" if provider else f"{clean_name} online course"
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def recommend_courses(user_interests: str, top_n: int = 5) -> list:
    user_vector = vectorizer.transform([user_interests])
    predicted_cluster = kmeans.predict(user_vector)[0]

    cluster_df = df[df["cluster"] == predicted_cluster].copy()
    cluster_vectors = vectorizer.transform(cluster_df["skills"])
    similarity_scores = cosine_similarity(user_vector, cluster_vectors).flatten()
    cluster_df["similarity"] = similarity_scores

    ranked = cluster_df.sort_values(by=["similarity", "rating"], ascending=[False, False]).head(top_n)
    results = ranked[["course_id", "course_name", "level", "rating", "similarity", "cluster"]].to_dict(orient="records")

    for course in results:
        course["youtube_link"] = generate_youtube_link(course["course_name"])
        course["course_search_link"] = generate_course_search_link(course["course_name"])

    return results



def build_roadmap(course_ids):
    course_map = df.set_index("course_id").to_dict(orient="index")
    visited = []
    result = []
    def visit(cid):
        if cid in visited or cid not in course_map:
            return
        visited.append(cid)
        for prereq in course_map[cid]["prerequisites"]:
            visit(prereq)
        result.append(cid)
    for cid in course_ids:
        visit(cid)
    roadmap = []
    for i, cid in enumerate(result, start=1):
        roadmap.append({
            "step": i, "course_id": cid,
            "course_name": course_map[cid]["course_name"],
            "level": course_map[cid]["level"]
        })
    return roadmap





def check_unlock_next(current_score, threshold=75.0):
    unlocked = current_score >= threshold
    return {
        "score": current_score, "threshold": threshold,
        "unlocked_next_module": unlocked,
        "message": "Great job! Next module unlocked." if unlocked
                    else f"Score {current_score}% is below {threshold}%. Revise and retry."
    }





def generate_learning_path(user_profile):
    skill_gap = analyze_skill_gap(user_profile["current_skills"], user_profile["required_skills"])
    recommended = recommend_courses(user_profile["interests"], top_n=5)
    course_ids = [c["course_id"] for c in recommended]
    roadmap = build_roadmap(course_ids)
    return {
        "user": user_profile["name"],
        "goal": user_profile["goal"],
        "skill_gap_analysis": skill_gap,
        "recommended_courses": recommended,
        "learning_roadmap": roadmap
    }





sample_user = {
    "name": "Aarav Sharma",
    "goal": "Data Scientist",
    "current_skills": {"Python": "Basic", "SQL": "Beginner", "Statistics": "None"},
    "interests": "python data analysis machine learning statistics",
    "required_skills": ["Python", "Statistics", "SQL", "Machine Learning"]
}

output = generate_learning_path(sample_user)
print(json.dumps(output, indent=2))






