# NPC - Neural Processing Companion

## Introduction

NPC is a gaming copilot - an agent that watches your screen, understands the game context (location, stats, items), and answers questions via voice to help you play better. Ask about boss strategies, where to go, what to do, and get instant spoken answers.

## Tech Stack

- **OpenAI API** - GPT-5.1 for game state analysis and query responses
- **Redis** - Vector store for game knowledge (scraped from wikis)
- **Eleven Labs** - Speech-to-text and text-to-speech

### Architecture

Two agents running in parallel:

1. **Game State Agent** - Continuously captures screenshots and maintains internal state (player location, stats, items)
2. **Voice Agent** - Handles voice queries, combines game context with RAG retrieval over the knowledge base

## Live Demo

Game: **Expedition 33**

### Example 1: Boss Strategy

**Scene:** Boss Fight  
**Timestamp:** 1:55  
**Prompt:** "What's a good strategy for this boss?"  
**Link:** [YouTube](https://youtu.be/YifTqomTZ_w?si=HD54r68B6aq6lOOA&t=115)

**Response:**
> This is Globu. Focus on lightning and flower control. Keep Gustave on overcharge and Looney on Thunderfall to stack lightning, add burn when safe, and constantly shoot the blue and red flowers as soon as they spawn, since they're immune to AoE, but keeping them down prevents shields and big heals. Then parry its limb combo strings to build gradient and use gradient attacks during its growth phases to break and burst it down.

---

### Example 2: Area Navigation

**Scene:** Gestral Village  
**Timestamp:** 27:47  
**Prompts:**

- "What are the things I should do here?"
- "How far into the game am I?"

**Link:** [YouTube](https://youtu.be/7gGgr6B4huk?si=Dvx0QtyeFHFszNTW&t=1666)

**Response:**
> This path in Gastral Village leads up toward the central village hub and shops. Push forward to reach NPCs, merchants and side paths branching deeper into the area.

**Scene:** Manor Kitchen  
**Prompt:** "Help, I'm a bit stuck. What can I do here?"

**Response:**
> You're in the manor kitchen where a secret basement can be opened. Interact with the three specific objects here: the statue, the pen, and the candle holder to reveal the hidden door and head down.

---

### Example 3: Build Optimization

**Scene:** Lune Build  
**Timestamp:** 8:00  
**Prompt:** "What's the best weapon given my build?"  
**Link:** [YouTube](https://youtu.be/JtI-L4r-veI?si=4_WG71FA713eZvAI&t=480)

---

### Example 4: Object Location

**Scene:** Mime  
**Timestamp:** 0:21  
**Prompt:** "Where is the Mime in this zone?"  
**Link:** [YouTube](https://youtu.be/z0JQhA-7bow?si=LQWafH2T4Q8pv3MT&t=21)

---
