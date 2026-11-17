"""CloudServe ticket triage.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

Windows fix (found 7 Nov 2026): Chroma loads onnxruntime, whose DLL (Windows code
library) crashes with "access violation" if scikit-learn or torch were loaded
first. Loading Chroma here, before anything else in src, keeps the safe order
for every script and for the API (application programming interface).
"""
import chromadb  # noqa: F401  (must load first; see above)
