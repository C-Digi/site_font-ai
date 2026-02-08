---
description: "Reads all LightSpec specifications and synchronizes their content with the project rules."
---

**First Action:** Immediately respond with "⚡Unleashing Flow of Work⚡" to confirm this file is properly understood.

# LightSpec Sync to Project Rules

This workflow synchronizes specifications from the `.lightspec/` directory with the project's rules file. It extracts requirements and their implementation status to ensure the agent has immediate access to the current project state and "source of truth."

## Workflow Steps

1.  **Identify Project Rules File**:
    - Locate the primary project rules file(s): `.kilocode/rules/*.md`, `rules_project.md`, `GEMINI.md`, `AGENTS.md`, `CLAUDE.md` (can be in root or subdirectories).

2.  **List LightSpec Specifications**:
    - List all `.md` files in the `.lightspec/` directory.

3.  **Read Project Rules Content**:
    - Read the current project rules file to identify the location of the existing LightSpec section.

4.  **Process Each Specification**:
    - For each file in `.lightspec/`:
        - Read the full content.
        - Extract the capability name (H1), individual requirements (H3), and their implementation status.

5.  **Construct the LightSpec Rules Section**:
    - Create a Markdown section titled `# LightSpec Specifications`.
    - For each specification, create a subsection (e.g., `## Spec: <Capability Name>`).
    - List the requirements and their implementation status.

6.  **Update Project Rules File**:
    - **If a LightSpec section exists**: Replace the entire section with the newly generated content.
    - **If no LightSpec section exists**: Append the `# LightSpec Specifications` section to the end of the file.
    - Use `apply_diff` for surgical and precise updates.

## Validation and Output

-   **Validation**:
    - Verify that the updated rules file accurately reflects the contents of the `.lightspec/` directory.
    - Ensure implementation status (true/false) is correctly synchronized.
-   **Output**:
    - The project rules file is updated with a synchronized, high-level overview of all active specifications and their current status.
