# 🛠️ CICD Automation Skill

**Skill ID:** `Skill_CICDAutomation_v1.0`
**Goal:** To manage deployment tasks, specifically triggering the restart of the FastAPI RAG backend or notifying a GitHub Actions workflow after a successful operation.

## 💻 Core Function Signature
`trigger_deployment_action(action_type: str, service_name: str) -> bool`

## ⚙️ Function Description
Executes a secure shell command or an API call to the CI/CD environment to perform the required action.

## 🔑 Usage Context
Used primarily by the **Vector_Index_Manager** agent.