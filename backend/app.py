import os
import json
import re
import urllib.parse
from database import init_db
from auth import router as auth_router

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Personalized Learning Path Recommender"
)
init_db()
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD DATASET
# ============================================================

DATASET_PATH = "courses_dataset_final.csv"

df = pd.read_csv(DATASET_PATH)

df = df.fillna("")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def search_link(skill):
    query = f"{skill} tutorial course"

    return (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )


def youtube_link(skill):
    query = f"{skill} tutorial"

    return (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )


# ============================================================
# FIND DATASET COURSES
# ============================================================

def find_courses_for_skill(skill, limit=3):

    skill = clean_text(skill)

    if not skill:
        return []


    # Search in multiple columns
    columns = [
        "course_name",
        "skills",
        "category",
        "description",
        "tags"
    ]


    scores = []


    for index, row in df.iterrows():

        text = " ".join(
            str(row[column])
            for column in columns
        )

        text = clean_text(text)


        # Exact skill match gets highest priority
        if skill in text:

            score = 3

        else:

            # Match individual words
            skill_words = skill.split()

            matches = sum(
                1
                for word in skill_words
                if len(word) > 2 and word in text
            )

            score = matches


        if score > 0:

            scores.append(
                (
                    score,
                    index
                )
            )


    # Highest score first
    scores.sort(
        key=lambda x: x[0],
        reverse=True
    )


    courses = []

    used_ids = set()


    for score, index in scores:

        row = df.iloc[index]

        course_id = str(
            row["course_id"]
        )


        # Prevent duplicate courses
        if course_id in used_ids:
            continue


        used_ids.add(course_id)


        courses.append({

            "course_id":
                course_id,

            "course_name":
                str(row["course_name"]),

            "level":
                str(row["level"]),

            "rating":
                float(row["rating"])
                if str(row["rating"]).replace(
                    ".",
                    "",
                    1
                ).isdigit()
                else 0,

            "duration_hours":
                str(row["duration_hours"]),

            "category":
                str(row["category"]),

            "skill":
                skill,

            "match_score":
                score,

            "course_search_link":
                search_link(
                    str(row["course_name"])
                ),

            "youtube_link":
                youtube_link(
                    str(row["course_name"])
                )
        })


        if len(courses) >= limit:
            break


    return courses


# ============================================================
# GROQ AI ANALYSIS
# ============================================================

def analyze_with_ai(
    goal,
    current_skills
):

    prompt = f"""
You are an expert career learning-path planner.

The user wants to achieve this goal:

GOAL:
{goal}

The user's current skills are:

CURRENT SKILLS:
{json.dumps(current_skills, indent=2)}

Your task is to analyze the career goal and create a personalized
learning plan.

IMPORTANT RULES:

1. Identify the important skills genuinely required for the goal.
2. Do NOT restrict the skills to any dataset.
3. Include modern industry-relevant skills.
4. For every required skill, determine the user's current level.
5. If the user does not know a skill, level must be "None".
6. Convert levels into percentages using EXACTLY:

None = 0
Basic = 25
Beginner = 35
Intermediate = 60
Advanced = 80
Expert = 95

7. Do not invent that the user knows a skill unless their input
   clearly indicates it.
8. Identify the required target level for every skill.
9. Calculate the skill gap.
10. Give every skill a status:
    - Strong
    - Needs Work
    - Major Gap
    - Not Started
11. Prioritize the largest gaps first.
12. Do not create or invent courses.
13. The backend will separately search the course dataset.
14. Return ONLY valid JSON.
15. Do not include markdown.
16. Do not include ```json.

Return exactly this structure:

{{
    "goal": "string",
    "timeline_days": number,
    "skills": [
        {{
            "name": "string",
            "current_level": "None | Basic | Beginner | Intermediate | Advanced | Expert",
            "current_percentage": number,
            "required_level": "Basic | Intermediate | Advanced | Expert",
            "required_percentage": number,
            "gap_percentage": number,
            "status": "Strong | Needs Work | Major Gap | Not Started",
            "priority": "High | Medium | Low"
        }}
    ],
    "overall_readiness": number,
    "insight": "string"
}}
"""


    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[

            {
                "role": "system",
                "content":
                    "You are a precise career learning-path AI. "
                    "Always return valid JSON."
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )


    content = response.choices[
        0
    ].message.content.strip()


    # Remove accidental markdown fences
    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"^```\s*",
        "",
        content
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )


    return json.loads(content)


# ============================================================
# COMPLETE RECOMMENDATION
# ============================================================

def generate_recommendation(
    user_profile
):

    goal = user_profile.get(
        "goal",
        ""
    )

    current_skills = user_profile.get(
        "current_skills",
        {}
    )


    if not goal:

        return {
            "error":
                "Goal is required."
        }


    # --------------------------------------------------------
    # STEP 1: AI ANALYSIS
    # --------------------------------------------------------

    ai_result = analyze_with_ai(
        goal,
        current_skills
    )


    # --------------------------------------------------------
    # STEP 2: FIND COURSES FOR EACH SKILL
    # --------------------------------------------------------

    all_courses = []

    used_course_ids = set()


    for skill in ai_result["skills"]:

        skill_name = skill["name"]

        courses = find_courses_for_skill(
            skill_name,
            limit=3
        )


        skill["courses_available"] = (
            len(courses) > 0
        )


        skill["courses"] = []


        for course in courses:

            course_id = course[
                "course_id"
            ]


            if course_id in used_course_ids:
                continue


            used_course_ids.add(
                course_id
            )


            skill["courses"].append(
                course
            )

            all_courses.append(
                course
            )


    # --------------------------------------------------------
    # STEP 3: MISSING SKILLS
    # --------------------------------------------------------

    missing_skills = []


    for skill in ai_result["skills"]:

        if not skill["courses_available"]:

            missing_skills.append({

                "skill":
                    skill["name"],

                "message":
                    "No matching course found in the current dataset.",

                "learning_link":
                    search_link(
                        skill["name"]
                    ),

                "youtube_link":
                    youtube_link(
                        skill["name"]
                    )
            })


    # --------------------------------------------------------
    # STEP 4: ROADMAP
    # --------------------------------------------------------

    roadmap = []

    step = 1


    # High priority first
    sorted_skills = sorted(
        ai_result["skills"],
        key=lambda x: (
            {
                "High": 0,
                "Medium": 1,
                "Low": 2
            }.get(
                x["priority"],
                3
            ),
            x["current_percentage"]
        )
    )


    for skill in sorted_skills:

        courses = skill.get(
            "courses",
            []
        )


        for course in courses:

            roadmap.append({

                "step":
                    step,

                "skill":
                    skill["name"],

                "course_id":
                    course["course_id"],

                "course_name":
                    course["course_name"],

                "level":
                    course["level"],

                "duration_hours":
                    course["duration_hours"],

                "rating":
                    course["rating"],

                "reason":
                    f"Recommended to improve {skill['name']}",

                "course_search_link":
                    course[
                        "course_search_link"
                    ],

                "youtube_link":
                    course[
                        "youtube_link"
                    ]
            })


            step += 1


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "user":
            user_profile.get(
                "name",
                "Learner"
            ),

        "goal":
            ai_result["goal"],

        "timeline_days":
            ai_result["timeline_days"],

        "overall_readiness":
            ai_result["overall_readiness"],

        "skills":
            ai_result["skills"],

        "insight":
            ai_result["insight"],

        "recommended_courses":
            all_courses,

        "missing_skills":
            missing_skills,

        "learning_roadmap":
            roadmap
    }


# ============================================================
# API ROUTES
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "Personalized Learning Platform API is running"
    }


@app.post("/recommend")
def recommend(
    user_profile: dict
):

    try:

        result = generate_recommendation(
            user_profile
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }
# ============================================================
# AI LEARNING ASSISTANT
# ============================================================

# ============================================================
# AI LEARNING ASSISTANT
# ============================================================

@app.post("/assistant")
def ai_assistant(data: dict):

    question = data.get("question", "").strip()

    if not question:
        return {
            "answer": "Please ask me a learning or career-related question."
        }

    # ========================================================
    # USER CONTEXT
    # Keep context SHORT to avoid Groq token-limit errors
    # ========================================================

    goal = str(data.get("goal", "")).strip()

    skills = data.get("skills", [])

    roadmap = data.get("roadmap", [])


    # ========================================================
    # COMPACT SKILLS
    # ========================================================

    compact_skills = []

    if isinstance(skills, list):

        for skill in skills[:12]:

            if isinstance(skill, dict):

                compact_skills.append({
                    "name": skill.get("name", ""),
                    "current": skill.get(
                        "current_percentage",
                        0
                    ),
                    "required": skill.get(
                        "required_percentage",
                        0
                    ),
                    "status": skill.get(
                        "status",
                        ""
                    ),
                    "priority": skill.get(
                        "priority",
                        ""
                    )
                })


    # ========================================================
    # COMPACT ROADMAP
    # Only send information useful to the assistant
    # ========================================================

    compact_roadmap = []

    if isinstance(roadmap, list):

        for item in roadmap[:8]:

            if isinstance(item, dict):

                compact_roadmap.append({
                    "step": item.get(
                        "step",
                        ""
                    ),
                    "skill": item.get(
                        "skill",
                        ""
                    ),
                    "course": item.get(
                        "course_name",
                        ""
                    ),
                    "level": item.get(
                        "level",
                        ""
                    ),
                    "duration": item.get(
                        "duration_hours",
                        ""
                    )
                })


    # ========================================================
    # CONTEXT
    # ========================================================

    context = f"""
GOAL:
{goal}

SKILLS:
{json.dumps(compact_skills)}

ROADMAP:
{json.dumps(compact_roadmap)}
"""


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = """
You are SkillRoute AI, a friendly learning and career assistant.

Your job is to help the user understand:

- Their learning roadmap
- Skill gaps
- Courses
- Programming
- Data Analytics
- Data Science
- Machine Learning
- Artificial Intelligence
- Web Development
- App Development
- Projects
- Interview preparation
- Career preparation

IMPORTANT RULES:

1. Use the user's goal and skills when relevant.

2. Give simple, beginner-friendly explanations.

3. Keep answers concise and easy to read.

4. Do not overwhelm the user with unnecessary information.

5. If the user asks what to learn next, prioritize their biggest skill gaps.

6. If the user asks about their roadmap, use the roadmap provided.

7. If the user asks a technical question, explain it simply
   and give a small example when useful.

8. If the user asks for steps, use numbered steps.

9. Do not invent courses or claim that a specific course exists
   unless it is provided in the user's context.

10. Be encouraging and practical.

11. Prefer short paragraphs and bullet points.

12. Avoid very long answers unless the user explicitly asks
    for detailed explanation.

13. If the question is unrelated to learning, technology,
    education or career, politely explain that SkillRoute AI
    is mainly designed for learning and career assistance.
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
Here is the user's SkillRoute information:

{context}

User's question:

{question}

Answer naturally as SkillRoute AI.

Make the answer easy to understand and directly useful.
"""


    # ========================================================
    # GROQ REQUEST
    # ========================================================

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_prompt
                }

            ],

            temperature=0.4,

            max_tokens=500
        )


        answer = response.choices[0].message.content.strip()


        return {
            "answer": answer
        }


    except Exception as e:

        print("AI ASSISTANT ERROR:", e)

        return {
            "answer": "I'm having trouble responding right now. Please try again in a moment.",
            "error": str(e)
        }