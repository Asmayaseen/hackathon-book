# 🛠️ Docusaurus Navigator Skill

**Skill ID:** `Skill_DocusaurusNavigator_v1.0`
**Goal:** To manage and validate the Docusaurus sidebar structure, file paths, and relative links within the textbook content.

## 💻 Core Function Signature
`validate_sidebar_entry(chapter_path: str, module_name: str) -> bool`

## ⚙️ Function Description
Checks if the chapter_path is correctly referenced in the Docusaurus sidebars.js file under the specified module_name.

## 🔑 Usage Context
Used primarily by the **Chapter_Composer** agent.