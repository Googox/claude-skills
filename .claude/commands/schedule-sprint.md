---
description: Plan a sprint and create all ceremony events in Google Calendar using cs-scrum-master + Calendar MCP
---

Route to **cs-scrum-master → Calendar MCP**.

1. Ask the user for: sprint start date, sprint length (default 2 weeks), team timezone, and working hours (if not in $ARGUMENTS).

2. **Check calendar for conflicts:**
   - Use `mcp__f9560b50-7433-4f35-b83d-5aff260238d9__list_calendars` to find the team calendar
   - Use `mcp__f9560b50-7433-4f35-b83d-5aff260238d9__list_events` for the sprint period to identify conflicts

3. **Find optimal time slots:**
   - Use `mcp__f9560b50-7433-4f35-b83d-5aff260238d9__suggest_time` for each ceremony type
   - Prefer mornings for planning/review, avoid Mondays 9am and Fridays 4pm for demos

4. **Read the scrum master skill for ceremony structure:**
   ```bash
   cat project-management/scrum-master/SKILL.md
   ```

5. **Structure the sprint ceremonies:**
   - Sprint Planning: 2–4 hours, Day 1 morning
   - Daily Standup: 15 min, every working day (same time)
   - Sprint Review/Demo: 1–2 hours, last day afternoon
   - Retrospective: 1 hour, last day (after review)
   - Backlog Refinement: 1 hour, mid-sprint

6. **Create all events in Calendar** (confirm with user before creating):
   - Use `mcp__f9560b50-7433-4f35-b83d-5aff260238d9__create_event` for each ceremony
   - Include: title, description with agenda, duration, recurrence (standups)
   - Add video conferencing link placeholder in description

7. **Deliver:** Sprint calendar summary with all ceremony times confirmed + agenda for each.
