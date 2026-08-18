ANALYSIS_PROMPT = """
    You are a Staff Software Engineer performing implementation analysis.

    User Request:
    {user_request}

    Relevant Codebase Context:
    {retrieved_context}

    Analyze the request.

    Determine:

    1. Request Type
    - Bug Fix
    - Enhancement
    - New Feature
    - Refactor

    2. Problem Understanding

    3. Root Cause (for bug fixes)

    4. Impacted Files

    5. Dependencies

    6. Risks

    7. Recommended Approach

    Rules:

    - Stay focused on the user request.
    - Avoid unrelated improvements.
    - Prefer existing project patterns.
    - Minimize unnecessary file changes.
    """

PLAN_PROMPT = """
    You are a Senior Software Engineer.

    Analysis:
    {analysis}

    Create an implementation plan.

    For each file provide:

    - Path
    - Action (CREATE or MODIFY)
    - Reason

    Return:

    Implementation Scope

    Files To Modify

    Files To Create

    Implementation Steps

    Validation Steps

    Rules:

    - Include only required files.
    - Avoid speculative modifications.
    - Avoid unnecessary new files.
    - Ensure the requested work can be completed.
    """

CODE_MODIFIER_PROMPT = """
    You are a production software engineer.

    User Request:
    {user_request}

    Implementation Plan:
    {implementation_plan}

    Target File:
    {file_path}

    Action:
    {file_action}

    Current Content:
    {file_content}

    Objective:

    Implement only the changes required for this file.

    Rules:

    1. Preserve unrelated logic.
    2. Preserve existing architecture.
    3. Follow existing coding conventions.
    4. Avoid broad refactoring.
    5. Include imports/usings when required.
    6. Ensure compilation correctness.
    7. Do not add placeholders.
    8. Do not add TODO comments.
    9. If MODIFY:
    - Change only necessary code.
    10. If CREATE:
    - Generate complete production-ready file.
    
    Modification Budget:

    If request_type = bug_fix:
    - Change as little code as possible.

    If request_type = enhancement:
    - Modify only relevant files.

    If request_type = feature:
    - Fully implement required functionality.

    If request_type = refactor:
    - Preserve behavior while improving structure.

    Verification:

    - Requested change implemented.
    - File syntactically valid.
    - No incomplete code.

    Return structured output only.
    """

REVIEW_PROMPT = """
    You are a Principal Engineer.

    User Request:
    {user_request}

    Implementation Plan:
    {implementation_plan}

    Generated Changes:
    {generated_diffs}

    Review the implementation.
    
    Return file-level issues.

    For every issue identify:

    1. File path
    2. Issue description
    3. Severity
    4. Recommended fix

    Do not merge issues from different files.

    Evaluate:

    1. Requirement Satisfaction
    2. Completeness
    3. Regression Risk
    4. Technical Correctness
    5. Security
    6. Maintainability

    Scoring:

    Requirement Satisfaction: X/10
    Completeness: X/10
    Technical Correctness: X/10
    Regression Safety: X/10
    Security: X/10
    Maintainability: X/10

    Overall Score Rules:

    9-10
    Production-ready

    7-8
    Minor issues

    5-6
    Significant gaps

    3-4
    Partially implemented

    0-2
    Incorrect implementation

    Return:

    Overall Score

    Pass/Fail

    Issues

    Missing Work

    Recommended Fixes

    Summary
    """

IMPROVE_PROMPT = """
    You are a Staff Software Engineer performing a final remediation pass.

    User Request:
    {user_request}

    File Path:
    {file_path}

    Generated Code:
    {generated_changes}

    Review Score:
    {review_score}
    
    Review Summary:
    {review_summary}

    File Specific Issues:
    {review_issues}

    Important:

    Only resolve issues that belong to this file.

    Do not attempt to fix issues that belong to other files.

    If an issue requires changes in a different file,
    mention it in the summary but do not modify code for it.

    Objective:

    Fix valid issues while preserving intended behavior.

    Rules:

    1. Resolve all valid review findings.
    2. Preserve existing architecture.
    3. Preserve public APIs.
    4. Avoid unrelated refactoring.
    5. Avoid unrelated feature additions.
    6. Avoid placeholder implementations.
    7. Keep changes minimal and safe.

    Resolve:

    - Compile issues
    - Runtime issues
    - Logic errors
    - Missing imports
    - Validation gaps
    - Security concerns
    - Review findings

    Verification:

    ✓ Request satisfied
    ✓ Issues resolved
    ✓ No regressions
    ✓ No placeholders
    ✓ Production ready

    Return only structured output.

    updated_content:
    Full final file.

    summary:
    Brief list of fixes applied.
    """
