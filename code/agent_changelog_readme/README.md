# Agent Changelog

This directory contains a machine-readable changelog (`changelog.json`) for tracking all changes made by AI agents.

## Schema

Each entry in `changelog.json` follows this structure:

| Field         | Type       | Description                                           |
|---------------|------------|-------------------------------------------------------|
| `id`          | string     | UUID v4 unique identifier                             |
| `timestamp`   | string     | ISO 8601 timestamp                                    |
| `agent`       | string     | Agent identifier (e.g., "github-copilot")             |
| `action`      | string     | One of: created, modified, deleted, moved, refactored |
| `files`       | string[]   | List of affected file paths (relative to project root)|
| `summary`     | string     | One-line description of what was done                 |
| `context`     | string     | Why it was done / user request context                |
| `status`      | string     | One of: complete, partial, needs_review               |
| `dependencies`| string[]   | IDs of related changelog entries                      |
| `notes`       | string     | Loose ends, next steps, or caveats                    |

## Usage

Agents should append to `changelog.json` after completing work. The dashboard reads this file to display change history.
