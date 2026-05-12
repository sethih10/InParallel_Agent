# In Parallel MCP Developer Guide

**Endpoint:** `https://www.in-parallel.ai/mcp`  
**Audience:** Developers building AI assistants, internal copilots, workflow automations, and agentic experiences on top of In Parallel work context.

> Note: This guide is drafted as a practical developer-facing reference for the In Parallel MCP direction, based on the latest Marketing and Management meeting context plus the currently exposed In Parallel workspace capabilities. The exact public endpoint behavior, authentication scheme, and tool schemas should be verified against the live MCP server.

---

## 1. What the In Parallel MCP does

The In Parallel MCP gives AI clients structured access to organizational execution context.

In practical terms, it lets an AI assistant answer questions and perform workflows around:

- Workspaces
- Meeting records
- Meeting summaries
- Speaker-attributed transcripts
- Decisions
- Action items
- Execution plans
- Plan version history

The core value is simple:

> In Parallel makes work context usable by AI.

Instead of asking an AI model to guess from generic knowledge, the MCP gives it access to the actual operating context behind a team’s meetings, decisions, commitments, and plans.

---

## 2. What developers can build with it

### 2.1 Meeting intelligence

Build assistants that can answer questions like:

- “What happened in the last Marketing meeting?”
- “What were the key decisions from the latest Management Weekly?”
- “Who attended the last Product Leadership meeting?”
- “Show me the action items created in yesterday’s meeting.”
- “Summarize the last five meetings for this workspace.”
- “What did we decide about pricing?”

### 2.2 Decision tracking

Build decision-aware workflows:

- List decisions by workspace.
- Retrieve full decision context.
- Identify who made or owned a decision.
- Trace a decision back to the meeting where it originated.
- Compare current decisions with older execution-plan versions.
- Surface unresolved, proposed, approved, or rejected decisions.

### 2.3 Action-item automation

Build execution workflows:

- List pending, assigned, in-progress, completed, cancelled, or archived action items.
- Retrieve a specific action item with its source context.
- Create new action items from a meeting.
- Update owners, statuses, summaries, and due dates.
- Close an action item with a resolution note.
- Build daily or weekly follow-up agents.

### 2.4 Execution-plan copilots

Build plan-aware assistants:

- Retrieve the current execution plan for a workspace.
- Show how the plan has changed over time.
- Explain why a plan shifted based on meeting decisions.
- Generate next-meeting checklists.
- Create weekly execution status summaries.
- Help teams prepare for leadership reviews.

### 2.5 Onboarding and context recovery

Build “catch me up” experiences:

- “Catch me up on this workspace.”
- “What are the open risks?”
- “What decisions led to this plan?”
- “What did I miss while I was away?”
- “What is the current state of the Marketing launch plan?”
- “What are the next commitments before the next meeting?”

### 2.6 Sales, customer, and leadership workflows

Build role-specific copilots:

- Sales: summarize account meetings and next steps.
- Customer success: identify customer commitments and unresolved follow-ups.
- Product: track feature decisions and delivery ownership.
- Leadership: summarize cross-functional execution risks.
- Operations: monitor overdue commitments and plan drift.

---

## 3. MCP concept overview

MCP, or Model Context Protocol, is a standard way for AI clients to connect to external tools and context sources.

An MCP setup usually has three parts:

1. **MCP host**  
   The AI application, such as an assistant, IDE, agent platform, or internal app.

2. **MCP client**  
   The component inside the host that communicates with the MCP server.

3. **MCP server**  
   The service that exposes tools, resources, and prompts to the AI client.

For In Parallel, the MCP server is the interface that exposes work context and execution workflows.

---

## 4. Transport and connection model

The In Parallel endpoint is expected to behave like a remote MCP server:

```text
https://www.in-parallel.ai/mcp
```

Modern remote MCP servers typically use **Streamable HTTP**. MCP also supports local `stdio` servers, but a hosted endpoint like this is normally connected over HTTP.

A typical MCP client configuration points to the endpoint and, depending on the client, includes either OAuth or a bearer token.

---

## 5. Authentication

The live authentication method should be verified against the In Parallel MCP server.

Recommended supported options:

### 5.1 OAuth

Best for end-user clients such as ChatGPT, Claude, Cursor, or other MCP-aware tools where users connect their own In Parallel account.

Expected behavior:

1. User adds the In Parallel MCP connector.
2. Client opens an OAuth authorization flow.
3. User authorizes access.
4. MCP client receives access and can call tools according to user permissions.

### 5.2 Bearer token

Best for server-side applications, automation, and internal tools.

Example header:

```http
Authorization: Bearer YOUR_IN_PARALLEL_API_KEY
```

### 5.3 Permission model

The MCP should respect the authenticated user’s workspace access. A user should only be able to see meetings, decisions, plans, and action items they are authorized to access in In Parallel.

---

## 6. Example MCP client configurations

These examples assume a remote HTTP MCP server. Exact support varies by client.

### 6.1 Cursor

Add this to `~/.cursor/mcp.json` or a project-level `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "url": "https://www.in-parallel.ai/mcp"
    }
  }
}
```

With bearer-token authentication via a local proxy such as `mcp-remote`:

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://www.in-parallel.ai/mcp",
        "--header",
        "authorization: Bearer YOUR_IN_PARALLEL_API_KEY"
      ]
    }
  }
}
```

### 6.2 VS Code

Workspace-level `.vscode/mcp.json`:

```json
{
  "servers": {
    "In Parallel MCP": {
      "type": "http",
      "url": "https://www.in-parallel.ai/mcp"
    }
  }
}
```

### 6.3 Claude Desktop / Claude.ai

Use custom connector settings where available:

```text
Name: In Parallel MCP
URL: https://www.in-parallel.ai/mcp
Authentication: OAuth
```

If OAuth is unavailable, use a local proxy pattern:

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://www.in-parallel.ai/mcp",
        "--header",
        "authorization: Bearer YOUR_IN_PARALLEL_API_KEY"
      ]
    }
  }
}
```

### 6.4 Cline

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "url": "https://www.in-parallel.ai/mcp",
      "type": "streamableHttp"
    }
  }
}
```

### 6.5 Windsurf

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "serverUrl": "https://www.in-parallel.ai/mcp"
    }
  }
}
```

### 6.6 Generic HTTP MCP client

```json
{
  "name": "In Parallel MCP",
  "type": "http",
  "url": "https://www.in-parallel.ai/mcp",
  "headers": {
    "Authorization": "Bearer YOUR_IN_PARALLEL_API_KEY"
  }
}
```

---

## 7. Tool reference

The following tool set reflects the current In Parallel execution-context capabilities available through the connected environment.

### 7.1 `list_workspaces`

Lists all workspaces accessible to the authenticated user.

**Use when:** The assistant needs to identify the workspace before retrieving meetings, decisions, action items, or plans.

**Example user requests:**

- “Show my In Parallel workspaces.”
- “Which teams can I access?”
- “Find the Marketing workspace.”

**Returns:**

- Workspace ID
- Workspace name
- Workspace category
- Owner, when available
- Parent workspace, when available

---

### 7.2 `list_meeting_records`

Lists recent meetings for a workspace, ordered newest first.

**Use when:** The assistant needs to find the latest meeting or browse recent meeting history.

**Inputs:**

- `workspace_id`
- Optional `page_cursor`

**Example user requests:**

- “What was our last Marketing meeting?”
- “Show recent meetings for Management Team.”
- “Find the latest Product Leadership meeting.”

**Returns:**

- Meeting ID
- Topic
- Platform
- Start and end time
- Organizer, when available
- Workspace name

---

### 7.3 `get_meeting_record`

Retrieves the complete structured record for a meeting.

**Use when:** The assistant needs the richest meeting view, including summary, decisions, action items, and attendees.

**Inputs:**

- `meeting_id`

**Example user requests:**

- “Summarize the last Marketing meeting.”
- “What action items came out of this meeting?”
- “What decisions were made in the last Management Weekly?”

**Returns:**

- Meeting topic
- Platform
- Start and end time
- AI-generated summary
- Attendees
- Decisions
- Action items
- Workspace name

---

### 7.4 `get_transcript`

Retrieves the speaker-attributed transcript for a meeting.

**Use when:** The assistant needs exact wording, speaker attribution, or detailed conversation context.

**Inputs:**

- `meeting_id`

**Example user requests:**

- “What exactly did Kristian say about MCP?”
- “Show the transcript for the last Marketing meeting.”
- “Find the part where pricing was discussed.”

**Returns:**

- Timestamped transcript
- Speaker-attributed conversation

**Guidance:** Prefer `get_meeting_record` for summaries and structured outputs. Use `get_transcript` when exact wording matters.

---

### 7.5 `list_decisions`

Lists decisions within a workspace.

**Use when:** The assistant needs to review what has been decided, proposed, approved, rejected, or is under review.

**Inputs:**

- `workspace_id`
- Optional `status`
- Optional `page_cursor`

**Supported statuses:**

- `proposed`
- `reviewing`
- `approved`
- `rejected`

**Example user requests:**

- “What decisions have we made in Marketing?”
- “Show proposed decisions in Product.”
- “What was decided about pricing?”

---

### 7.6 `get_decision`

Retrieves the full details of a specific decision.

**Use when:** The assistant needs rationale, context, origin, or owner information for a decision.

**Inputs:**

- `decision_id`

**Example user requests:**

- “Give me the context behind this decision.”
- “Who decided this and why?”
- “Which meeting did this decision come from?”

---

### 7.7 `list_action_items`

Lists action items within a workspace.

**Use when:** The assistant needs to show tasks, open work, due dates, or owner assignments.

**Inputs:**

- `workspace_id`
- Optional `status`
- Optional `start_date`
- Optional `end_date`
- Optional `page_cursor`

**Supported statuses:**

- `backlog`
- `assigned`
- `in_progress`
- `done`
- `archived`
- `cancelled`

**Example user requests:**

- “What are my open action items?”
- “What is overdue in Marketing?”
- “Show in-progress tasks for Management Team.”
- “What is due this week?”

---

### 7.8 `get_action_item`

Retrieves the full details and context of an action item.

**Use when:** The assistant needs to drill into a specific task.

**Inputs:**

- `action_item_id`

**Example user requests:**

- “What is this action item about?”
- “Where did this task come from?”
- “Who owns this and when is it due?”

---

### 7.9 `create_action_item`

Creates a new action item in a workspace, linked to a source meeting.

**Use when:** A meeting produced a concrete task that should be tracked.

**Inputs:**

- `workspace_id`
- `source_meeting_id`
- `title`
- Optional `summary`
- Optional `owner_email`
- Optional `due_date`
- Optional `status`

**Example user requests:**

- “Create an action item for Sami to draft the MCP launch post.”
- “Add a task from this meeting to restore analytics.”
- “Assign Kristian to follow up on WhySummit feedback.”

**Important:** Every action item should trace back to a source meeting.

---

### 7.10 `update_action_item`

Updates an existing action item.

**Use when:** Work has started, ownership changes, scope changes, or a due date moves.

**Inputs:**

- `action_item_id`
- Optional `title`
- Optional `summary`
- Optional `owner_email`
- Optional `due_date`
- Optional `status`

**Example user requests:**

- “Move this task to in progress.”
- “Reassign this to Barbara.”
- “Change the due date to next Friday.”
- “Update the description with the latest context.”

---

### 7.11 `close_action_item`

Marks an action item as done and adds a processed timestamp.

**Use when:** Work is complete.

**Inputs:**

- `action_item_id`
- Optional `resolution`

**Example user requests:**

- “Close this action item.”
- “Mark the analytics task as done.”
- “Close it with the note: GA tag restored and verified.”

---

### 7.12 `get_execution_plan`

Retrieves the current execution plan for a workspace.

**Use when:** The assistant needs the living roadmap or operating plan for a workspace.

**Inputs:**

- `workspace_id`

**Example user requests:**

- “What is the current Marketing plan?”
- “Show the execution plan for Product.”
- “What are we working toward in this workspace?”

**Returns:**

- Plan title
- Workspace
- Last updated time
- Plan content, when available

---

### 7.13 `get_plan_versions`

Retrieves version history for a workspace’s execution plan.

**Use when:** The assistant needs to explain how the plan has changed over time.

**Inputs:**

- `workspace_id`

**Example user requests:**

- “How has the Marketing plan changed?”
- “What changed after the latest Management meeting?”
- “Show earlier versions of this plan.”

---

## 8. Recommended agent behavior

### 8.1 Start with workspace resolution

When a user asks about a team, project, or recurring meeting:

1. Call `list_workspaces`.
2. Match the user’s phrase to a workspace name.
3. If there are multiple likely matches, ask a short clarification.
4. Use the selected `workspace_id` for subsequent calls.

### 8.2 Prefer structured meeting records before transcripts

Use `get_meeting_record` first for:

- Summaries
- Action items
- Decisions
- Attendees
- Next steps

Use `get_transcript` only when:

- The user asks who said what.
- Exact language matters.
- The summary does not contain enough detail.

### 8.3 Preserve traceability

When generating answers from In Parallel data, include:

- Workspace name
- Meeting title
- Meeting date
- Decision or action item owner
- Due date, when available
- Source meeting, when relevant

### 8.4 Avoid over-fetching

For common requests:

- Latest meeting summary: `list_meeting_records` → `get_meeting_record`
- Open tasks: `list_action_items`
- Decision detail: `list_decisions` → `get_decision`
- Plan status: `get_execution_plan`
- What changed: `get_plan_versions`

---

## 9. Common workflows

### 9.1 “What happened in the last Marketing meeting?”

1. `list_workspaces`
2. Identify `Marketing`.
3. `list_meeting_records(workspace_id="marketing-weekly")`
4. Select the newest meeting.
5. `get_meeting_record(meeting_id)`
6. Return summary, decisions, and action items.

### 9.2 “Create follow-up tasks from this meeting”

1. `get_meeting_record(meeting_id)`
2. Identify missing or explicit tasks.
3. Confirm owner and due date if missing.
4. `create_action_item(...)`
5. Return the created task list.

### 9.3 “What changed in the plan?”

1. `get_execution_plan(workspace_id)`
2. `get_plan_versions(workspace_id)`
3. Compare current and previous versions.
4. Summarize changes and likely drivers.
5. Link changes back to decisions or meetings when possible.

### 9.4 “Prepare me for the next meeting”

1. `list_meeting_records(workspace_id)`
2. `get_meeting_record(latest_meeting_id)`
3. `list_action_items(workspace_id, status="assigned")`
4. `list_decisions(workspace_id)`
5. Return:
   - Open items
   - Recent decisions
   - Risks
   - Suggested agenda
   - Follow-up checklist

### 9.5 “What should I follow up on this week?”

1. `list_workspaces`
2. For relevant workspace(s), call `list_action_items`.
3. Filter by due date and status.
4. Group by owner, due date, and urgency.
5. Return the follow-up plan.

---

## 10. Example prompts for users

### Meeting questions

- “Summarize the latest Marketing Weekly.”
- “What was discussed in the last Management Team meeting?”
- “Show me the decisions from the latest Product Leadership meeting.”
- “Who attended the last Board meeting?”

### Execution questions

- “What are the open action items in Marketing?”
- “What is overdue this week?”
- “What changed in the execution plan?”
- “What should we review in the next meeting?”

### Decision questions

- “What decisions are still proposed?”
- “What did we decide about MCP positioning?”
- “Who owns the decision on pricing?”

### Automation requests

- “Create an action item for Sami to draft the launch blog post.”
- “Move the website analytics task to in progress.”
- “Close the WhySummit feedback task.”
- “Create a checklist from the latest meeting.”

---

## 11. Error handling

### Workspace not found

Response pattern:

> I could not find a workspace that matches that name. I found these close matches: Marketing, Management Team, Product Leadership. Which one should I use?

### No meetings found

Response pattern:

> I found the workspace, but I do not see any meeting records in it yet.

### Missing permissions

Response pattern:

> I cannot access that workspace or meeting with the current account. Check that the user has access in In Parallel.

### Missing owner email

Response pattern:

> I can create the action item, but I need a valid owner email from the In Parallel tenant to assign it.

### Ambiguous action item

Response pattern:

> I found more than one matching action item. Please choose which one to update.

---

## 12. Security and privacy guidance

### 12.1 Respect user permissions

Never expose workspace, meeting, or action-item data outside the authenticated user’s permissions.

### 12.2 Avoid unnecessary transcript access

Transcripts may contain sensitive discussion. Prefer structured summaries unless exact wording is required.

### 12.3 Avoid leaking private context into prompts

If integrating with an LLM, send only the context needed to answer the user’s question.

### 12.4 Log carefully

Do not log full transcripts, confidential decisions, or sensitive action-item summaries unless there is a clear operational reason and the logs are protected.

### 12.5 Validate write operations

For create, update, or close actions, confirm the intended change before executing if the user’s instruction is ambiguous.

---

## 13. Implementation checklist

Before publishing the MCP publicly, verify:

- [ ] Endpoint is reachable at `https://www.in-parallel.ai/mcp`.
- [ ] Streamable HTTP transport works across target clients.
- [ ] OAuth flow works for user-facing clients.
- [ ] Bearer token flow works for programmatic clients.
- [ ] Tool discovery returns stable names and schemas.
- [ ] Workspace access is permission-scoped.
- [ ] Meeting records are redacted or protected where needed.
- [ ] Transcript access is appropriately permissioned.
- [ ] Action-item write operations are auditable.
- [ ] Errors are clear and safe.
- [ ] Rate limits are documented.
- [ ] Versioning strategy is documented.
- [ ] Example client configurations are tested.

---

## 14. Suggested public documentation structure

Recommended pages for `www.in-parallel.ai/mcp`:

1. **Overview**
   - What the In Parallel MCP does
   - Who it is for
   - Example use cases

2. **Quickstart**
   - Connect from Cursor, Claude, VS Code, Cline, Windsurf, ChatGPT
   - Authentication options
   - First query

3. **Tool Reference**
   - Workspace tools
   - Meeting tools
   - Decision tools
   - Action-item tools
   - Execution-plan tools

4. **Guides**
   - Build a meeting-summary assistant
   - Build an action-item follow-up agent
   - Build a plan-review copilot
   - Build a leadership briefing bot

5. **Security**
   - Auth
   - Permissions
   - Transcript handling
   - Write operation safety

6. **Changelog**
   - Tool additions
   - Schema updates
   - Breaking changes

---

## 15. Sample public quickstart

### Step 1: Add the MCP server

```json
{
  "mcpServers": {
    "In Parallel MCP": {
      "url": "https://www.in-parallel.ai/mcp"
    }
  }
}
```

### Step 2: Authenticate

Use OAuth if your client supports it. For server-side usage, provide a bearer token:

```http
Authorization: Bearer YOUR_IN_PARALLEL_API_KEY
```

### Step 3: Ask your first question

Try:

```text
What workspaces can I access in In Parallel?
```

Then:

```text
Summarize the latest Marketing meeting and list open action items.
```

### Step 4: Build a workflow

Example:

```text
Each Friday, summarize open action items in the Marketing workspace, group them by owner, and identify what needs attention before Monday.
```

---

## 16. Developer examples

### 16.1 Workspace discovery

```text
User: What teams can I access?

Agent:
1. Calls list_workspaces.
2. Returns workspace names grouped by category.
3. Suggests common next actions.
```

### 16.2 Latest meeting summary

```text
User: What happened in the last Marketing meeting?

Agent:
1. Calls list_meeting_records for Marketing.
2. Gets the newest meeting ID.
3. Calls get_meeting_record.
4. Summarizes discussion, decisions, and action items.
```

### 16.3 Action-item update

```text
User: Mark the Google Analytics task as in progress.

Agent:
1. Calls list_action_items for Marketing.
2. Finds matching task.
3. If match is clear, calls update_action_item with status="in_progress".
4. Confirms the update.
```

### 16.4 Plan review

```text
User: What should we focus on in the next Marketing meeting?

Agent:
1. Gets the latest meeting record.
2. Lists open action items.
3. Retrieves the current execution plan.
4. Returns agenda recommendations.
```

---

## 17. Versioning recommendations

Use stable tool names and additive schema changes wherever possible.

Recommended versioning pattern:

- Keep the MCP endpoint stable: `/mcp`
- Add tool fields without removing existing ones.
- Deprecate fields before removal.
- Document breaking changes in a changelog.
- Consider including a `server_version` field in metadata or resource output.

---

## 18. What to build first

The best first developer-facing demos are:

1. **Latest Meeting Briefing**
   - Finds the latest meeting in a workspace.
   - Summarizes decisions and action items.

2. **Action Item Follow-up Agent**
   - Lists assigned or overdue tasks.
   - Groups by owner and due date.
   - Updates statuses.

3. **Execution Plan Copilot**
   - Retrieves the current plan.
   - Compares plan versions.
   - Explains what changed.

4. **Leadership Weekly Brief**
   - Summarizes recent meetings, decisions, open risks, and overdue actions across selected workspaces.

---

## 19. Positioning for developers

Use this message:

> In Parallel MCP lets developers build AI agents that understand real organizational context: meetings, decisions, action items, and execution plans.

Short version:

> Build AI assistants that understand what your team discussed, decided, and committed to.

Developer value props:

- No need to build custom meeting-context integrations.
- Structured access to workspaces, meetings, decisions, actions, and plans.
- Traceable context from meeting to task to plan.
- Read and write workflows for execution follow-through.
- Useful for internal copilots, leadership agents, sales assistants, and project execution bots.


---

## References

- Model Context Protocol transport specification: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports
- Model Context Protocol overview: https://modelcontextprotocol.io/
Basically, you can simulate the API with notes too. 

