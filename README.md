# AI Code Agent

An intelligent AI-powered software engineering assistant that analyzes existing codebases, understands user requirements, generates code changes, reviews its own output, and safely applies modifications through a Human-in-the-Loop workflow.

The agent leverages **LangGraph**, **LLMs**, and a multi-step software development pipeline to assist developers in implementing new features, fixing bugs, refactoring code, and improving code quality while maintaining safety and transparency.

---

## 🖥️ Project Preview

The interface lets a developer submit a feature or bug request, review the proposed changes in a side-by-side code diff, and explicitly approve or reject the update before any files are modified.

![AI Code Agent project preview](ai-code-agent-preview.png)

---

## 🚀 Features

### 📂 Codebase Analysis
- Scans project directories recursively
- Extracts project structure and relevant source files
- Builds contextual understanding of the codebase

### 🧠 Intelligent Planning
- Analyzes user requests
- Identifies impacted files
- Generates implementation plans before modifying code
- Supports:
  - Feature Development
  - Bug Fixes
  - Code Improvements
  - Refactoring

### ✍️ Code Generation
- Creates new files when required
- Modifies existing files
- Produces complete updated content
- Maintains project conventions and architecture

### 🔍 AI Code Review
- Reviews generated changes
- Detects:
  - Logical issues
  - Potential bugs
  - Missing implementations
  - Code quality concerns
- Generates detailed review feedback

### 🔄 Improvement Loop
- Uses review feedback to improve generated code
- Performs iterative refinement before approval

### 📋 Diff Generation
- Creates Git-style code diffs
- Highlights file-level changes
- Allows easy review before applying updates

### 👨‍💻 Human-in-the-Loop Approval
- Displays generated changes
- Requires explicit user approval
- Supports:
  - Approve
  - Reject
  - Request Improvements

### 🛡️ Safe File Updates
- Creates backups before modifying files
- Prevents accidental code loss
- Supports rollback if needed

### ✅ Automated Validation
- Detects project test commands
- Executes tests after applying changes
- Reports failures for additional corrections

---

## 🏗️ Architecture

```text
User Request
      │
      ▼
Request Classification
      │
      ▼
Project Scan
      │
      ▼
Implementation Planning
      │
      ▼
Generate Changes
      │
      ▼
Review Changes
      │
      ▼
Improve Changes
      │
      ▼
Generate Diffs
      │
      ▼
Human Approval
      │
      ├── Reject
      │
      ├── Improve Again
      │
      ▼
Apply Changes
      │
      ▼
Run Tests
      │
      ▼
Complete
```

---

## 🛠️ Technology Stack

### Backend

- Python 3.11+
- LangGraph
- LangChain
- Azure OpenAI / OpenAI
- Pydantic
- AsyncIO

### AI Components

- Structured Output Generation
- Code Review Agent
- Planning Agent
- Improvement Agent
- File Selection Agent

### Frontend

- Streamlit (Current UI)
- React/Angular (Future UI Option)

---

## 📁 Project Structure

```text
ai-code-agent/
│
├── app.py
├── graph.py
├── state.py
│
├── nodes/
│   ├── scan_project_node.py
│   ├── classify_request_node.py
│   ├── plan_node.py
│   ├── generate_changes_node.py
│   ├── review_node.py
│   ├── improve_node.py
│   ├── generate_diff_node.py
│   ├── human_approval_node.py
│   ├── apply_changes_node.py
│   └── run_tests_node.py
│
├── prompts/
│   ├── feature_prompts.py
│   ├── fix_prompts.py
│   ├── improve_prompts.py
│   └── review_prompts.py
│
├── models/
│   ├── implementation_plan.py
│   ├── generated_changes.py
│   ├── review_result.py
│   └── state_models.py
│
├── backups/
│
├── tests/
│
└── README.md
```

---

## 🔄 Supported Request Types

### Feature Development

```text
Add JWT authentication to the API
```

### Bug Fix

```text
Fix null reference exception in UserService
```

### Code Improvement

```text
Improve performance of the search endpoint
```

### Refactoring

```text
Refactor repository layer to use dependency injection
```

---

## Example Workflow

### User Request

```text
Create JWT authentication for the application
```

### Agent Actions

1. Scans project structure
2. Finds authentication-related files
3. Generates implementation plan
4. Creates or modifies required files
5. Reviews generated code
6. Improves identified issues
7. Generates diffs
8. Waits for approval
9. Applies changes
10. Runs tests
11. Returns results

---

## Human Approval Flow

Before modifying files, the agent presents:

- Modified files
- New files
- Generated diffs
- Review findings

Example:

```text
Files to Modify:
- Program.cs
- appsettings.json

Files to Create:
- JwtService.cs
- JwtOptions.cs

Review Score:
92/100

Approve? (Y/N)
```

---

## Safety Mechanisms

### File Backup

Before any modification:

```text
UserService.cs
    ↓
UserService.cs.backup
```

### Approval Gate

No code is written until user approval is received.

### Review Validation

Every generated change passes through an AI review process before application.

### Test Verification

Tests are executed after updates to catch potential issues immediately.

---

## Future Enhancements

- Multi-Agent Architecture
- Tool Calling Support
- Git Integration
- Automatic Pull Request Creation
- React Diff Viewer
- VS Code Extension
- Repository-Level Memory
- RAG-based Code Retrieval
- Parallel File Processing
- Docker Support
- Multi-Language Support

---

## Why This Project?

Traditional code generation tools focus only on generating code.

This AI Code Agent goes beyond generation by introducing:

✅ Planning  
✅ Review  
✅ Improvement  
✅ Human Approval  
✅ Safe Application  
✅ Automated Validation

It behaves more like an autonomous software engineering assistant than a simple code completion tool.

---

## Author

**Ashim Chowdhury**

Senior Software Engineer | AI Engineering Enthusiast

Skills:
- Python
- LangGraph
- LangChain
- Azure OpenAI
- GoogleGenerativeAI
- Streamlit
- Streamlit Code Diff
- Agentic AI Systems

---

## License

This project is licensed under the MIT License.
