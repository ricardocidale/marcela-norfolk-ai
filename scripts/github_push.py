#!/usr/bin/env python3
"""
Push local git changes to GitHub using the GitHub REST API.
Works with fine-grained tokens that don't support git HTTPS push.
"""
import os
import subprocess
import base64
import json
import requests

TOKEN = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
REPO = "Norfolk-Group/marcela-norfolk-ai"
BRANCH = "master"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}
BASE = "https://api.github.com"

def api(method, path, **kwargs):
    r = requests.request(method, f"{BASE}{path}", headers=HEADERS, **kwargs)
    r.raise_for_status()
    return r.json()

def get_file_content(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Files to push
files_to_push = [
    "api/index.py",
    "scripts/extract_docs.py",
    "scripts/ingest_kb.py",
    "scripts/setup_neon.py",
]

repo_root = "/home/ubuntu/marcela-norfolk-ai"

print(f"Pushing to {REPO}:{BRANCH}")

# Get current branch SHA
ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
current_sha = ref["object"]["sha"]
print(f"Current HEAD: {current_sha[:8]}")

# Get the current tree
commit = api("GET", f"/repos/{REPO}/git/commits/{current_sha}")
tree_sha = commit["tree"]["sha"]
print(f"Current tree: {tree_sha[:8]}")

# Create blobs for each file
tree_items = []
for rel_path in files_to_push:
    full_path = os.path.join(repo_root, rel_path)
    if not os.path.exists(full_path):
        print(f"  SKIP (not found): {rel_path}")
        continue
    
    content = get_file_content(full_path)
    blob = api("POST", f"/repos/{REPO}/git/blobs", json={
        "content": content,
        "encoding": "base64"
    })
    tree_items.append({
        "path": rel_path,
        "mode": "100644",
        "type": "blob",
        "sha": blob["sha"]
    })
    print(f"  Blob created: {rel_path} ({blob['sha'][:8]})")

# Create new tree
new_tree = api("POST", f"/repos/{REPO}/git/trees", json={
    "base_tree": tree_sha,
    "tree": tree_items
})
print(f"New tree: {new_tree['sha'][:8]}")

# Create commit
commit_message = """feat: Neon pgvector RAG + persistent memory + Mel Robbins voice

- Wire Neon PostgreSQL as persistent conversation store (conversations table)
- Wire Neon pgvector as RAG knowledge base (knowledge_base table, 105 chunks)
- 6 Norfolk AI docs ingested: NorfolkAISolutionsOverview, norfolk-ai-content,
  KnowledgeBenefitsofAIAgents, SuperConversationsKnowledgeBase,
  WhatAreSuperConversations, SuperConversationsFoundation
- Embeddings: gemini-embedding-001 (3072 dims), HNSW index on halfvec
- RAG retrieval: top-4 chunks by cosine similarity injected into every prompt
- Persistent memory: conversation history stored in Neon, survives cold starts
- Mel Robbins-inspired voice: direct, warm, witty, action-oriented
- Platform-specific system prompts: WhatsApp, Slack, Telegram
- Health endpoint reports DB status and KB chunk count
- Requires DATABASE_URL env var in Vercel"""

new_commit = api("POST", f"/repos/{REPO}/git/commits", json={
    "message": commit_message,
    "tree": new_tree["sha"],
    "parents": [current_sha]
})
print(f"New commit: {new_commit['sha'][:8]}")

# Update the branch reference
api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", json={
    "sha": new_commit["sha"],
    "force": False
})
print(f"\n✓ Successfully pushed to {REPO}:{BRANCH}")
print(f"  Commit: {new_commit['sha']}")
print(f"  Message: {commit_message.splitlines()[0]}")
print(f"\nVercel will auto-deploy from this commit.")
