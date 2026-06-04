# MCP Server Integrations

Maps the available MCP servers to cs-* agents and slash commands.

**Last Updated:** June 2026

---

## Available MCP Servers

| Service | MCP Prefix | Slash Commands | Agents |
|---------|------------|---------------|--------|
| **Gmail** | `mcp__5c59a741-*` | `/email-draft` | cs-content-creator, cs-demand-gen-specialist |
| **Calendar** | `mcp__f9560b50-*` | `/schedule-sprint` | cs-scrum-master, cs-product-manager |
| **Notion** | `mcp__ced01181-*` | `/save-to-notion` | All agents |
| **HubSpot** | `mcp__8f2d65aa-*` | `/campaign-report`, `/plan-campaign` | cs-demand-gen-specialist |
| **Contact Enrichment** | `mcp__0b3a87ea-*` | `/plan-campaign` | cs-demand-gen-specialist |
| **Company/Job Data** | `mcp__4c66a764-*` | `/ceo-brief`, `/cto-review` | cs-ceo-advisor, cs-cto-advisor |

---

## Gmail (`mcp__5c59a741-7084-4188-a9af-4546d6957875__*`)

### Read tools (auto-allowed)
| Tool | Purpose |
|------|---------|
| `search_threads` | Search email threads by query |
| `get_thread` | Read a specific email thread |
| `list_labels` | List all Gmail labels |
| `list_drafts` | List existing drafts |

### Write tools (require confirmation)
| Tool | Purpose |
|------|---------|
| `create_draft` | Create a new email draft |
| `create_label` | Create a new label |
| `label_thread` | Apply a label to a thread |

### Integration pattern — `/email-draft`
```
1. search_threads (find relevant context)
2. cs-content-creator (draft the email copy)
3. create_draft (save to Gmail)
```

---

## Calendar (`mcp__f9560b50-7433-4f35-b83d-5aff260238d9__*`)

### Read tools (auto-allowed)
| Tool | Purpose |
|------|---------|
| `list_calendars` | List all available calendars |
| `list_events` | List events in a date range |
| `get_event` | Get details of a specific event |
| `suggest_time` | Suggest available time slots |

### Write tools (require confirmation)
| Tool | Purpose |
|------|---------|
| `create_event` | Create a new calendar event |
| `update_event` | Update an existing event |
| `respond_to_event` | Accept/decline an invitation |

### Integration pattern — `/schedule-sprint`
```
1. list_events (check for conflicts)
2. suggest_time (find open slots)
3. cs-scrum-master (structure the sprint ceremonies)
4. create_event (book: planning, daily standups, review, retro)
```

---

## Notion (`mcp__ced01181-861e-4906-ab56-c4389119e8b1__*`)

### Read tools (auto-allowed)
| Tool | Purpose |
|------|---------|
| `search` | Search pages and databases |
| `fetch` | Read a specific page |
| `get_comments` | Read page comments |
| `get_teams` | List workspace teams |
| `get_users` | List workspace users |

### Write tools (require confirmation)
| Tool | Purpose |
|------|---------|
| `create_pages` | Create one or more pages |
| `update_page` | Update page content |
| `create_database` | Create a new database |
| `create_comment` | Add a comment to a page |

### Integration pattern — `/save-to-notion`
```
1. search (find the target page or database)
2. <any agent> (generate the content)
3. create_pages or update_page (save to Notion)
```

---

## HubSpot (`mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__*`)

### Read tools (auto-allowed)
| Tool | Purpose |
|------|---------|
| `get_campaign_analytics` | Campaign performance metrics |
| `get_campaign_asset_metrics` | Per-asset performance (emails, pages) |
| `get_campaign_contacts_by_type` | Contacts enrolled in a campaign |
| `get_crm_objects` | Get CRM records (contacts, companies, deals) |
| `search_crm_objects` | Search across CRM objects |
| `query_crm_data` | SQL-style queries on CRM data |
| `search_owners` | Find HubSpot owners |
| `get_organization_details` | Portal/org details |
| `get_user_details` | HubSpot user info |
| `get_properties` | Property definitions for an object type |
| `search_properties` | Find specific properties |

### Integration pattern — `/campaign-report`
```
1. get_campaign_analytics (pull performance data)
2. get_campaign_asset_metrics (per-asset breakdown)
3. cs-demand-gen-specialist (interpret and recommend actions)
```

### Integration pattern — `/plan-campaign`
```
1. query_crm_data (segment contacts for targeting)
2. search_crm_objects (find relevant company/contact context)
3. cs-demand-gen-specialist (strategy) → cs-content-creator (copy)
```

---

## Contact Enrichment (`mcp__0b3a87ea-6e00-4875-b1d6-c25f6164a800__*`)

### Tools
| Tool | Purpose |
|------|---------|
| `find-and-enrich-company` | Enrich company data (employees, funding, tech stack) |
| `find-and-enrich-contacts-at-company` | Find and enrich contacts at a company |
| `find-and-enrich-list-of-contacts` | Bulk contact enrichment |
| `ask-question-about-accounts` | Natural language query about accounts |
| `query-objects` | Query enriched data objects |

### Integration pattern — ABM campaigns
```
1. find-and-enrich-company (target account research)
2. find-and-enrich-contacts-at-company (find decision makers)
3. cs-demand-gen-specialist (personalised ABM strategy)
4. cs-content-creator (personalised outreach copy)
```

---

## Company & Job Data (`mcp__4c66a764-a169-49c4-9f7a-54180cb29c32__*`)

### Tools
| Tool | Purpose |
|------|---------|
| `get_company_data` | Company info (size, industry, funding, etc.) |
| `search_jobs` | Search open job postings |
| `get_job_details` | Details of a specific job |
| `get_resume` | Get resume/profile data |

### Integration pattern — competitive intelligence
```
1. get_company_data (competitor research)
2. search_jobs (infer competitor priorities from hiring)
3. cs-ceo-advisor (strategic competitive analysis)
```

---

## Cross-Agent MCP Workflow Map

| Task | MCPs Used | Agents |
|------|-----------|--------|
| ABM campaign | Contact Enrichment → HubSpot | cs-demand-gen + cs-content-creator |
| Campaign performance review | HubSpot analytics | cs-demand-gen-specialist |
| Sprint ceremonies scheduling | Calendar | cs-scrum-master |
| Document QMS findings | Notion | cs-regulatory-specialist |
| Email outreach draft | Gmail | cs-content-creator |
| Competitor analysis | Company Data | cs-ceo-advisor |
| Board deck research | Company Data + Contact Enrichment | cs-ceo-advisor |
