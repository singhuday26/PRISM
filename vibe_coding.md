# The Ultimate Guide to Vibe Coding with AntiGravity

"Vibe coding"—building software primarily through natural language and AI—has evolved rapidly. However, communication gaps can still lead to frustrating loops, especially when debugging or building complex features. If you find yourself having to repeat instructions or getting incomplete fixes, the issue is often related to missing context and implicit assumptions.

This guide provides a structured, step-by-step approach to giving optimal prompts, specifically tailored for working with agentic coding assistants like AntiGravity.

---

## Phase 1: Setting Up for Success (Context is King)
When developing a project, isolated prompts often fail because the agent lacks the broader picture. You know your app inside out, but the agent starts fresh.

1. **Provide the "Why" and "What":** Don't just declare *what* to do; explain *why* and give structural hints.
   * **Weak:** "Add a user profile page."
   * **Strong:** "We need a new User Profile page to allow users to update their avatar and bio. It should follow the same layout as the Settings page and fetch data from the `/api/user/profile` endpoint."
2. **Explicitly state boundaries:** Tell the agent what *not* to touch to prevent regressions.
   * **Example:** "Only modify the frontend React components. Do not change the backend API schema, as it's used by other services."
3. **Reference Specific Files:** Rather than letting the agent guess, point it exactly where to look.
   * **Example:** "Look at `src/components/UserProfile.tsx` and `src/api/user.ts`."

## Phase 2: Building New Features
Big features broken down into small, verifiable chunks succeed far more often than massive "do it all" prompts.

1. **The "Plan-First" Pattern:** For anything larger than a few lines of code, force the agent to plan before it acts.
   * **Prompt:** "I want to implement a new notification dropdown. Before writing code, please outline your implementation plan in a markdown list, detailing which files you will create or modify. Wait for my approval before proceeding."
2. **Step-by-Step Execution:** Ask the agent to build incrementally.
   * **Prompt:** "Let's build the notification dropdown. Step 1: Create the UI layout with mock data. Let me know when you've done this, and we'll move to Step 2 (API integration)."

## Phase 3: The Debugging Masterclass
Debugging is the hardest part of vibe coding because it requires exact state and context. When a feature fails and you ask the agent to fix it, it might guess blindly if you don't provide the right details.

### Anatomy of the Perfect Debugging Prompt
1. **Expected vs. Actual Behavior:** What did you want to happen? What actually happened?
2. **Exact Error Messages:** Provide the exact error message or stack trace.
3. **Reproduction Steps:** What exact sequence of clicks or actions caused the error?
4. **Environment Context:** Mention relevant logs or terminal output.

* **Weak Debugging Prompt:** "The login isn't working after you added the new feature. Fix it."
* **Strong Debugging Prompt:** "When I click the 'Login' button with valid credentials, the button shows a loading state forever and the user is never redirected to the dashboard. The browser console shows an error: `TypeError: Cannot read properties of undefined (reading 'token')` in `auth.ts:45`. The backend terminal shows a successful 200 OK response. Please investigate `auth.ts` and fix the token extraction logic."

### Breaking Out of the "Loop"
If the agent fails to fix a bug on the first or second try, **stop asking it to just "fix it"**. The agent is missing critical visibility.
* **Force Visibility:** "That fix didn't work. Please add expansive `console.log` statements in the relevant functions so we can see what the data actually looks like at runtime. I will run it and give you the logs."
* **Refocus:** "The error is exactly the same. Let's step back. Please use the `grep_search` and `view_file` tools to read the actual shape of our database model before trying another fix."

## Phase 4: Long-Term Optimal Workflow
1. **Use Architecture Documents:** Instead of keeping the project architecture in your head, have the agent document it. E.g., "Create an `ARCHITECTURE.md` file detailing our current routing layout and database schema." Reference this doc in future prompts.
2. **Regularly "Commit" Checkpoints:** When a feature works, clearly acknowledge it. "Great, the auth is working perfectly now. Let's move on to the next feature: the news feed." This mentally closes the context loop.
3. **Ask the Agent What Context It Needs:** When starting a complex task, flip the script and ask the agent to interrogate you.
   * **Prompt:** "I want to add a real-time chat feature. Before you start, what files do you need to look at, and what questions do you have for me regarding the technical design?"

## Summary Checklist for your Prompts
- [ ] Did I mention specific file names?
- [ ] Did I explain *how* I want it implemented, not just *what*?
- [ ] If debugging, did I provide the exact error logs?
- [ ] Is this task small enough to be completed in one go, or should I ask the agent for a plan first?
