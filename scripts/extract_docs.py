#!/usr/bin/env python3
"""
Extract and chunk Norfolk AI knowledge base documents.
Outputs a list of (source, chunk_text) tuples saved to chunks.json.
"""

import json
import os
import re
from pathlib import Path

# ── Extractors ──────────────────────────────────────────────────────────────

def extract_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_pdf(path: str) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def extract_md(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


# ── Chunking ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping chunks of ~chunk_size characters,
    breaking on sentence/paragraph boundaries where possible.
    """
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"[ \t]+", " ", text)

    # Split on paragraph breaks first, then sentences
    paragraphs = re.split(r"\n\n+", text)

    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph keeps us under limit, append
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            # Save current chunk if non-empty
            if current:
                chunks.append(current)
            # If paragraph itself is too long, split by sentences
            if len(para) > chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                current = ""
                for sent in sentences:
                    if len(current) + len(sent) + 1 <= chunk_size:
                        current = (current + " " + sent).strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
            else:
                current = para

    if current:
        chunks.append(current)

    # Add overlap: prepend tail of previous chunk to each chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            tail = chunks[i - 1][-overlap:]
            overlapped.append(tail + " " + chunks[i])
        chunks = overlapped

    return [c.strip() for c in chunks if len(c.strip()) > 50]


# ── Main ─────────────────────────────────────────────────────────────────────

UPLOAD_DIR = "/home/ubuntu/upload"

FILES = [
    ("NorfolkAISolutionsOverview.docx",
     "pasted_file_q4AD3v_NorfolkAISolutionsOverview.docx", "docx"),
    ("norfolk-ai-content.md",
     "pasted_file_avXqIi_norfolk-ai-content.md", "md"),
    ("KnowledgeBenefitsofAIAgents.pdf",
     "pasted_file_Fi5xu0_KnowledgeBenefitsofAIAgents1.pdf", "pdf"),
    ("SuperConversationsKnowledgeBase.pdf",
     "pasted_file_8aLDM3_SuperConversationsKnowledgeBase2.pdf", "pdf"),
    ("WhatAreSuperConversations.pdf",
     "pasted_file_6DiREz_WhatAreSuperConversations.pdf", "pdf"),
    ("SuperConversationsFoundation.docx",
     "pasted_file_Ax4SIL_SuperConversationsastheFoundationforBusinessSalesandAITraining.docx", "docx"),
]

all_chunks = []

for doc_name, filename, ftype in FILES:
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        print(f"  MISSING: {filename}")
        continue

    print(f"Extracting: {doc_name} ({ftype})")
    if ftype == "docx":
        text = extract_docx(path)
    elif ftype == "pdf":
        text = extract_pdf(path)
    elif ftype == "md":
        text = extract_md(path)
    else:
        continue

    chunks = chunk_text(text)
    print(f"  → {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "source": doc_name,
            "chunk_index": i,
            "text": chunk,
        })

print(f"\nTotal chunks: {len(all_chunks)}")

output_path = "/home/ubuntu/marcela-norfolk-ai/scripts/kb_chunks.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"Saved to {output_path}")
