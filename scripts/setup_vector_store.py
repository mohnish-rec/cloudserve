"""Setup Guide step 04: build the vector store from the documentation.

Follows the guide's code with five changes, each marked below:
the pack's field is doc_id (not id), the file is read as UTF-8,
the store is rebuilt from scratch so a second run gives the same result,
three library notices are switched off so the output stays clean,
and the chunk size is the one chosen in decision D-017.
Run: python scripts/setup_vector_store.py
"""
import json
import os
import shutil
import warnings
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
# Change 4: switched off before the libraries load.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")          # Chroma sends no usage data
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")   # Windows symlink notice
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")        # tokenizer fork notice

# sentence-transformers 2.2.2 (pinned by the pack) still calls this older function,
# which works in the huggingface-hub version we pin (requirements fix 5).
warnings.filterwarnings("ignore", message=".*cached_download.*", category=FutureWarning)

from langchain.text_splitter import RecursiveCharacterTextSplitter  # noqa: E402
from langchain_community.embeddings import HuggingFaceEmbeddings  # noqa: E402
from langchain_community.vectorstores import Chroma  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = (ROOT / os.environ["CHROMA_PATH"]).resolve()  # absolute path, as guide section 09 advises
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]

# Change 2: read as UTF-8.
with open(ROOT / "data" / "documentation.json", encoding="utf-8") as f:
    documents = json.load(f)

# Change 5: chunk size 400, overlap 80 (guide: 800 and 120), chosen in decision D-017
# after comparing three sizes on the development tickets (scripts/compare_retrieval.py).
splitter = RecursiveCharacterTextSplitter(chunk_size=int(os.getenv("CHUNK_SIZE", "400")),
                                          chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "80")))
texts, metadatas = [], []
for doc in documents:
    for chunk in splitter.split_text(doc["content"]):
        texts.append(chunk)
        # Change 1: the field is doc_id. Category added for routing later.
        metadatas.append({"doc_id": doc["doc_id"], "title": doc["title"], "category": doc["category"]})

# Change 3: start from an empty store every time.
if CHROMA_PATH.exists():
    shutil.rmtree(CHROMA_PATH)

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
store = Chroma.from_texts(
    texts=texts, metadatas=metadatas, embedding=embeddings,
    collection_name="cloudserve_docs",
    persist_directory=str(CHROMA_PATH),
)
store.persist()
print(f"stored {len(texts)} passages from {len(documents)} documents")

# Quick check that retrieval works (guide section 09: "Chroma returns no results").
best = store.similarity_search("How do I reset my password?", k=1)[0]
print("test query -> top result:", best.metadata["doc_id"], "|", best.metadata["title"])