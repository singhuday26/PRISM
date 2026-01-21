# 📘 The Product Engineer's Playbook
> **A Field Guide to Building Software Effectively**
> *Based on our PRISM Development Session*

To become a top-tier Product Engineer, you must master the art of moving from **Ambiguity** to **Impact**. Code is just the tool; the *process* is the product.

---

## Phase 1: Discovery (The "Why")
*Most products fail here because they build the wrong thing.*

### The Framework
1.  **Identify the User**: Not "everyone", but a specific person (e.g., "District Health Officer").
2.  **Find the "Hair on Fire" Problem**: What keeps them up at night? (e.g., "I get blamed for bed shortages").
3.  **Define the Job-to-be-Done (JTBD)**:
    > "When [Situation], I want to [Action], so that [Outcome]."

### PRISM Case Study
We started with a generic "Disease Dashboard". We paused, asked deep questions, and discovered the *real* problem was **logistics mismanagement**, not just awareness. This led to our **Panic-to-Power Pivot**.

---

## Phase 2: Definition (The "What")
*Translating vision into blueprints.*

### Artifacts You Need
1.  **Product Strategy**: The high-level vision (e.g., `PRISM_COMMAND_STRATEGY.md`).
2.  **Feature Specifications**: Detailed requirements (e.g., `FEATURE_RESOURCE_INTELLIGENCE.md`).
    - **P0 (Must Have)**: The core value (e.g., Resource Math).
    - **P1 (Nice to Have)**: The bells and whistles (e.g., Dark Mode).

### The "Product A vs Product B" Lesson
We realized we had two users with conflicting needs:
- **Authority**: Needs complex data & control (Product A).
- **Public**: Needs simple advice & speed (Product B).
*Lesson*: Don't built a "Swiss Army Knife". Build two focused surgical tools sharing the same handle.

---

## Phase 3: Execution Planning (The "How")
*Measure twice, cut once.*

### The Implementation Plan
Never start coding without a plan (like `implementation_plan.md`).
1.  **Schema First**: Define your data structure. Data is harder to change than code.
2.  **API Second**: Define the contract between Frontend and Backend.
3.  **Logic Third**: Write the core service.

### The "MVP" Mindset
**M**inimum **V**iable **P**roduct does not mean "broken". It means **Complete Core, No Fluff**.
- *PRISM MVP*: Better to have accurate math and no UI, than a beautiful UI with wrong math.

---

## Phase 4: Verification (The "Reality Check")
*Does it actually work?*

1.  **Seed Data**: You can't test a car without gas. Always build scripts to load realistic fake data (`seed_resources.py`).
2.  **Integration Testing**: Test the *flow*, not just functions.
3.  **Walkthroughs**: Prove it works (User Verification).

---

## Your Roadmap to Mastery

As you move to the Agent section to build PRISM, follow this loop:

1.  **Stop**: Don't code. Read the `STRATEGY.md`.
2.  **Think**: "What is the smallest step I can take to prove value?" (e.g., "Can I calculate bed demand correctly?")
3.  **Spec**: Write a mini-spec for that step.
4.  **Build**: Code it.
5.  **Verify**: Prove it.

*Welcome to Product Engineering.* 🚀
