# Skill: Refactoring

## Purpose
Improve existing code quality without changing functionality.

---

# Refactoring Goals

Improve:
- readability
- maintainability
- modularity
- performance
- consistency

Preserve:
- behavior
- functionality
- API compatibility

---

# Refactoring Rules

## Structure

Improve:
- folder organization
- module boundaries
- component separation
- service abstraction

---

## Code Cleanup

Remove:
- duplicated logic
- dead code
- unnecessary complexity
- unused imports

Simplify:
- conditionals
- loops
- abstractions

---

## Naming Improvements

Ensure:
- descriptive variable names
- meaningful function names
- consistent conventions

Avoid:
- abbreviations
- unclear identifiers

---

# Safety Rules

Before refactoring:
- understand current behavior
- inspect dependencies
- identify critical flows

After refactoring:
- run tests
- verify API responses
- validate edge cases

---

# Incremental Refactoring

Preferred:
- small safe changes
- isolated commits
- test-driven improvements

Avoid:
- massive rewrites
- architecture replacement without reason

---

# AI Agent Rules

Always:
- preserve backward compatibility
- improve readability first
- keep changes focused

Never:
- combine refactor with unrelated features
- silently change business logic