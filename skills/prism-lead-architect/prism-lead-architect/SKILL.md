---
name: prism-lead-architect
description: Senior architectural oversight for the PRISM project. Ensures FAANG-level standards, O(n) complexity, edge-case handling, and robust testing fixtures. Use when proposing architectural changes, adding new features, or refactoring core services.
---

# PRISM Lead Architect

This skill provides expert oversight for the PRISM project, ensuring that every code change adheres to the highest engineering standards and maintains alignment with the core project vision.

## 🏗️ Architectural Compliance
- **Core Intent (BLUEPRINT.md)**: Every change must align with the vision of PRISM as a multi-disease, regional surveillance platform. Prioritize layered isolation: Route -> Service -> Schema -> DB.
- **2026 Stack (STACK_SIGNATURE.md)**: Strictly use the library versions specified (FastAPI 0.110+, React 19, Tailwind 4). Avoid introducing new dependencies without justification.

## 🚀 FAANG-Level Engineering Standards
- **Algorithmic Efficiency**: Always aim for O(n) or O(n log n) complexity. Be critical of nested loops over large datasets (e.g., when processing time-series dataframes in `Pandas`).
- **Edge-Case Resilience**: Proactively handle missing climate data, database timeouts, and schema mismatches. Use custom exceptions from `backend/exceptions.py`.
- **Self-Documenting Code**: Code is documentation. Use descriptive variable names, comprehensive docstrings, and maintain a consistent style across the codebase.

## 🧪 Testing & Validation
- **Pytest Fixtures**: Automatically suggest or create new `pytest` fixtures for any added service logic. Ensure fixtures are stored in `tests/conftest.py` if they are reusable.
- **Isolation Checks**: Verify that new logic respects the multi-disease isolation principle—no cross-contamination of disease data.
- **Validation Mandate**: A feature is not complete until its corresponding tests in `tests/unit/` and `tests/integration/` are passing.

## 🧠 Workflows
1. **Research & Audit**: When asked to implement a feature, first audit the existing `BLUEPRINT.md` to see where it fits.
2. **Strategy Design**: Propose a plan that emphasizes performance and scalability (e.g., offloading data science tasks to async workers).
3. **Execution with Test-First**: Write the testing fixtures first, implement the logic, and then validate.
