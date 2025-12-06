# 🛠️ User Profile Fetcher

**Skill ID:** `Skill_UserProfileFetcher_v1.0`
**Goal:** To securely retrieve a specific user's detailed profile data (background questionnaire results) from the Neon Postgres database.

## 💻 Core Function Signature
`fetch_user_profile(user_id: str) -> dict`

## ⚙️ Function Description
Queries the user_profiles table using the provided user_id and returns the user's expertise level.

## 🔑 Usage Context
Used by the **Level_Adjuster** agent.