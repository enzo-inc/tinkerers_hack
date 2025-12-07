# Elden Ring Game State Agent

An AI agent that understands your Elden Ring game state using Redis as a vector database.

## Project Structure

```
├── redis_setup/          # Redis vector database setup
│   ├── data/npcs.json    # NPC seed data
│   └── setup_redis.py    # Populates Redis with embeddings
├── game_state_agent/     # Game state agent (TBD)
├── query_npcs.py         # Query utilities
└── README.md
```

## Prerequisites

**Redis Server** must be running locally:

```bash
# macOS
brew install redis
brew services start redis
```

## Setup

```bash
# Install dependencies
uv sync

# Populate the Redis database
uv run python redis_setup/setup_redis.py
```

## Redis Setup

The `redis_setup/` folder contains everything needed to populate Redis with Elden Ring NPC data.

## Query Examples

```bash
uv run python -i query_npcs.py
```

```python
from query_npcs import semantic_search, filter_search, get_npc

# Semantic search - natural language queries
semantic_search("tragic warrior bound by fate")
semantic_search("trickster who deceives travelers")

# Filter by metadata
filter_search("@region:{Limgrave}")
filter_search("@role:{Merchant}")
filter_search("@race:{Demigod}")

# Combined: semantic + filter
semantic_search("powerful warrior", filter_expr="@region:{Limgrave}")

# Get specific NPC by ID
get_npc("blaidd")
```

### NPC Data Schema

NPCs in `redis_setup/data/npcs.json` have:
- `name`, `race`, `role`, `region`
- `locations`, `affiliation`, `quest`
- `description`, `lore`, `dialogue`
- `is_hostile`, `becomes_hostile`, `drops`

### Adding NPCs

Edit `redis_setup/data/npcs.json` and re-run:
```bash
uv run python redis_setup/setup_redis.py
```
