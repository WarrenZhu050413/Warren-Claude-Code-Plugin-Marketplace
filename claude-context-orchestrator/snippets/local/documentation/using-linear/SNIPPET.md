---
description: Linear GraphQL API workflows with authentication, queries, mutations, and common patterns
SNIPPET_NAME: using-linear
ANNOUNCE_USAGE: true
---

# Linear Workflows & GraphQL API

## API Authentication
```bash
# Set your API key (get from https://linear.app/settings/api)
export LINEAR_API_KEY="lin_api_YOUR_KEY_HERE"
```

## Common Workflows

### 1. Creating Issues
```graphql
mutation CreateIssue {
  issueCreate(input: {
    title: "Issue title"
    description: "Issue description"
    teamId: "team-id"
    priority: 1  # 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
    stateId: "state-id"  # Optional
    assigneeId: "user-id"  # Optional
  }) {
    success
    issue {
      id
      identifier
      title
      url
    }
  }
}
```

### 2. Searching Issues
```graphql
query SearchIssues {
  issues(filter: {
    title: { contains: "search term" }
    # OR use: assignee: { id: { eq: "user-id" } }
    # OR use: state: { name: { eq: "In Progress" } }
  }) {
    nodes {
      id
      identifier
      title
      state { name }
      assignee { name }
      priority
      url
    }
  }
}
```

### 3. Updating Issues
```graphql
mutation UpdateIssue {
  issueUpdate(
    id: "issue-id"
    input: {
      stateId: "new-state-id"
      priority: 2
      assigneeId: "user-id"
    }
  ) {
    success
    issue {
      id
      identifier
      state { name }
    }
  }
}
```

### 4. Getting Teams & States
```graphql
query GetTeamsAndStates {
  teams {
    nodes {
      id
      name
      key
      states {
        nodes {
          id
          name
          type  # backlog, unstarted, started, completed, canceled
        }
      }
    }
  }
}
```

### 5. Getting Current User
```graphql
query Viewer {
  viewer {
    id
    name
    email
    assignedIssues {
      nodes {
        id
        identifier
        title
        state { name }
      }
    }
  }
}
```

## Quick cURL Examples

```bash
# Get viewer info
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}'

# Create issue
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueCreate(input: {title: \"New issue\", teamId: \"TEAM_ID\"}) { success issue { id identifier url } } }"}'
```

## Key Concepts

- **Teams**: Workspaces for organizing issues (teamId required for creating issues)
- **States**: Workflow stages (Backlog, Todo, In Progress, Done, Canceled)
- **Priorities**: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
- **Identifiers**: Human-readable issue IDs (e.g., "ENG-123")
- **Filters**: Powerful filtering on any field (nested conditions supported)

## Essential Links

**Official Documentation:**
- GraphQL API: https://developers.linear.app/docs/graphql/working-with-the-graphql-api
- GraphQL Schema Explorer: https://studio.apollographql.com/public/Linear-API/variant/current/home
- SDK (Node/TypeScript): https://github.com/linear/linear/tree/master/packages/sdk
- API Reference: https://developers.linear.app/docs/graphql/reference

**Interactive Tools:**
- GraphQL Playground: https://developers.linear.app/docs/graphql/working-with-the-graphql-api#graphql-playground
- API Explorer (requires login): Your workspace URL + /settings/api

**Guides:**
- Authentication: https://developers.linear.app/docs/graphql/authentication
- Pagination: https://developers.linear.app/docs/graphql/pagination
- Webhooks: https://developers.linear.app/docs/graphql/webhooks
- Rate Limits: https://developers.linear.app/docs/graphql/rate-limiting
