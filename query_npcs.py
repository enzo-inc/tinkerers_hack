"""
Query Elden Ring NPCs from Redis Vector Database
"""

import numpy as np
import redis
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

# --- Configuration ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
INDEX_NAME = "idx:npcs"
VECTOR_DIM = 768

# --- Connect ---
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
embedder = SentenceTransformer("msmarco-distilbert-base-v4")


def semantic_search(query_text, top_k=3, filter_expr="*"):
    """
    Search NPCs by semantic similarity.

    Args:
        query_text: Natural language query
        top_k: Number of results to return
        filter_expr: Optional filter (e.g., "@region:{Limgrave}")

    Returns:
        List of matching NPCs with scores
    """
    # Generate query embedding
    query_embedding = embedder.encode([query_text])[0].astype(np.float32)

    # Build query
    query = (
        Query(f"({filter_expr})=>[KNN {top_k} @embedding $query_vec AS score]")
        .sort_by("score")
        .return_fields("score", "name", "race", "role", "region", "description")
        .dialect(2)
    )

    # Execute
    results = client.ft(INDEX_NAME).search(
        query,
        {"query_vec": query_embedding.tobytes()}
    )

    return results.docs


def filter_search(filter_expr):
    """
    Search NPCs by metadata filters.

    Examples:
        "@region:{Limgrave}"
        "@role:{Merchant}"
        "@is_hostile:{true}"
        "@affiliation:{Ranni the Witch}"
    """
    query = Query(filter_expr).return_fields("name", "role", "region", "affiliation")
    return client.ft(INDEX_NAME).search(query).docs


def get_npc(npc_id):
    """Get a specific NPC by ID."""
    return client.hgetall(f"npc:{npc_id}")


def print_results(results, show_description=True):
    """Pretty print search results."""
    for i, doc in enumerate(results, 1):
        score = getattr(doc, 'score', None)
        score_str = f" (similarity: {1 - float(score):.2f})" if score else ""
        print(f"\n{i}. {doc.name}{score_str}")
        print(f"   Race: {doc.race} | Role: {doc.role} | Region: {doc.region}")
        if show_description and hasattr(doc, 'description'):
            desc = doc.description[:150] + "..." if len(doc.description) > 150 else doc.description
            print(f"   {desc}")


# --- Example Queries ---
if __name__ == "__main__":
    print("=" * 60)
    print("ELDEN RING NPC VECTOR DATABASE")
    print("=" * 60)

    # Semantic search examples
    print("\n### Semantic Search: 'tragic warrior bound by fate' ###")
    results = semantic_search("tragic warrior bound by fate")
    print_results(results)

    print("\n### Semantic Search: 'helpful merchant who sells items' ###")
    results = semantic_search("helpful merchant who sells items")
    print_results(results)

    print("\n### Semantic Search: 'mysterious woman with hidden purpose' ###")
    results = semantic_search("mysterious woman with hidden purpose")
    print_results(results)

    print("\n### Semantic Search: 'trickster who deceives travelers' ###")
    results = semantic_search("trickster who deceives travelers")
    print_results(results)

    # Filter search examples
    print("\n### Filter: NPCs in Limgrave ###")
    results = filter_search("@region:{Limgrave}")
    for doc in results:
        print(f"  - {doc.name} ({doc.role})")

    print("\n### Filter: Merchants ###")
    results = filter_search("@role:{Merchant}")
    for doc in results:
        print(f"  - {doc.name} in {doc.region}")

    print("\n### Filter: Demigods ###")
    results = filter_search("@race:{Demigod}")
    for doc in results:
        print(f"  - {doc.name} ({doc.affiliation})")

    # Combined: semantic + filter
    print("\n### Combined: 'powerful warrior' in Limgrave only ###")
    results = semantic_search("powerful warrior", filter_expr="@region:{Limgrave}")
    print_results(results)
