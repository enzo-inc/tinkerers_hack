"""
Elden Ring NPC Vector Database Setup
Loads NPC data into Redis with vector embeddings for semantic search.
"""

import json
import numpy as np
import redis
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

# --- Configuration ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
INDEX_NAME = "idx:npcs"
NPC_PREFIX = "npc:"
VECTOR_DIM = 768  # msmarco-distilbert-base-v4 output dimension

# --- Connect to Redis ---
# Note: decode_responses=False for binary vector data
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

print("Connected to Redis")

# --- Load NPC Data ---
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, "data/npcs.json"), "r") as f:
    npcs = json.load(f)

print(f"Loaded {len(npcs)} NPCs")

# --- Initialize Embedding Model ---
print("Loading embedding model (this may take a moment)...")
embedder = SentenceTransformer("msmarco-distilbert-base-v4")

# --- Create Embeddings ---
# Combine description + lore + dialogue for richer embeddings
def create_embedding_text(npc):
    parts = [
        npc.get("description", ""),
        npc.get("lore", ""),
        npc.get("dialogue", "")
    ]
    return " ".join(parts)

print("Generating embeddings...")
embedding_texts = [create_embedding_text(npc) for npc in npcs]
embeddings = embedder.encode(embedding_texts).astype(np.float32)

# --- Store NPCs in Redis ---
print("Storing NPCs in Redis...")
pipeline = client.pipeline()

for npc, embedding in zip(npcs, embeddings):
    key = f"{NPC_PREFIX}{npc['id']}"

    # Prepare document - convert lists to comma-separated strings for TAG fields
    doc = {
        "id": npc["id"],
        "name": npc["name"],
        "race": npc["race"],
        "role": npc["role"],
        "locations": ",".join(npc["locations"]),
        "region": npc["region"],
        "affiliation": npc["affiliation"],
        "quest": npc["quest"],
        "is_hostile": str(npc["is_hostile"]).lower(),
        "becomes_hostile": str(npc["becomes_hostile"]).lower(),
        "drops": ",".join(npc["drops"]) if npc["drops"] else "",
        "description": npc["description"],
        "lore": npc["lore"],
        "dialogue": npc["dialogue"],
        "embedding": embedding.tobytes()  # Store as raw bytes
    }

    pipeline.hset(key, mapping=doc)

pipeline.execute()
print(f"Stored {len(npcs)} NPCs")

# --- Create Search Index ---
print("Creating search index...")

# Drop existing index if it exists
try:
    client.ft(INDEX_NAME).dropindex(delete_documents=False)
    print("Dropped existing index")
except:
    pass

# Define schema
schema = (
    TextField("name", weight=2.0),
    TextField("description"),
    TextField("lore"),
    TextField("dialogue"),
    TagField("race"),
    TagField("role"),
    TagField("region"),
    TagField("affiliation"),
    TagField("quest"),
    TagField("is_hostile"),
    TagField("becomes_hostile"),
    VectorField(
        "embedding",
        "FLAT",
        {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": "COSINE",
        },
    ),
)

# Create index
client.ft(INDEX_NAME).create_index(
    schema,
    definition=IndexDefinition(prefix=[NPC_PREFIX], index_type=IndexType.HASH),
)

print(f"Created index: {INDEX_NAME}")
print("\n--- Setup Complete ---")
print(f"NPCs stored: {len(npcs)}")
print(f"Index: {INDEX_NAME}")
print(f"Key prefix: {NPC_PREFIX}")
