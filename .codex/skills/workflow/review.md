# Skill: Code Review

## Purpose
Review code quality, maintainability, correctness, and security.

---

# Review Objectives

Check for:
- bugs
- poor architecture
- security vulnerabilities
- readability issues
- duplicated logic
- performance problems

---

# Review Categories

## Code Quality

Verify:
- naming consistency
- modular structure
- clean logic flow
- proper abstractions

Avoid:
- deeply nested logic
- massive functions
- duplicated code

---

## Security Review

Check for:
- unsafe input handling
- missing validation
- exposed secrets
- insecure authentication
- SQL injection risks

Never allow:
- plaintext passwords
- hardcoded API keys
- unrestricted admin access

---

## Performance Review

Identify:
- unnecessary database calls
- blocking operations
- inefficient loops
- large payloads

Recommend:
- pagination
- caching
- indexing
- query optimization

---

## Maintainability Review

Verify:
- reusable components
- proper separation of concerns
- readable structure
- scalable organization

---

# Review Output Format

Use:

## Findings
- issue
- impact
- recommendation

## Severity
- low
- medium
- high
- critical

---

# AI Agent Rules

Always:
- explain WHY something is problematic
- provide improvement suggestions
- preserve project conventions

Never:
- rewrite unrelated code
- criticize without actionable feedback