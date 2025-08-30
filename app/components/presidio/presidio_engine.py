import re
import uuid

from presidio_analyzer import AnalyzerEngine
from rapidfuzz import fuzz
from sentence_transformers import util


class PresidioEngine:
    def __init__(self, model=None):
        self.model = model
        self.analyzer = AnalyzerEngine()
        self.entity_map = {}
        self.embeddings = {}  # store embeddings for fast similarity checks

    def analyze_text(self, text):
        # Analyze text using Presidio
        results = self.analyzer.analyze(text=text, language="en")
        # Map result of similar entities to a common entity uid
        for entity in results:
            entity_str = text[entity.start : entity.end]
            entity_type = entity.entity_type
            key = self.add_entity(entity_str, entity_type)
            print(
                f"Detected entity: {entity_str}, Type: {entity_type}. Key mapping: {key}"
            )
        print(f"Entity_map: {self.entity_map}")
        return self

    def anonymise_text(self, text):
        # Build list of (alias, key) pairs
        alias_key_pairs = []
        for key, data in self.entity_map.items():
            for alias in data["aliases"]:
                alias_key_pairs.append((alias, key))

        # Sort by alias length (longest first to prevent partial overlaps)
        alias_key_pairs.sort(key=lambda x: len(x[0]), reverse=True)

        # Replace aliases with keys
        for alias, key in alias_key_pairs:
            pattern = r"\b" + re.escape(alias) + r"\b"
            text = re.sub(pattern, key, text)
        return text

    def add_entity(self, text, entity_type, threshold=0.6):
        # new_emb = self.model.encode(text, convert_to_tensor=True)
        new_emb = self.model.encode(text)

        best_key, best_score = None, -1
        for key, emb in self.embeddings.items():
            existing = self.entity_map[key]["canonical"]

            # --- Regex direct search ---
            # direct substring check (regex word boundary)
            if re.search(rf"\b{re.escape(existing)}\b", text) or re.search(
                rf"\b{re.escape(text)}\b", existing
            ):
                score = 1.0  # strong match
            else:
                # Fuzzy similarity search (if regex fails)
                fuzz_score = fuzz.token_sort_ratio(text, existing) / 100
                score = fuzz_score

            # --- Embeddings similarity search (if fuzzy fails) ---
            if score < (threshold):
                score = util.cos_sim(new_emb, emb).item()
                # print(f"Embedding score '{text}' and '{existing}': {score:.2f}")
            # track best match
            if score > best_score:
                best_key, best_score = key, score

        # --- Merge into existing entity ---
        if best_score >= threshold:
            # Add new alias if not already stored
            if text not in self.entity_map[best_key]["aliases"]:
                self.entity_map[best_key]["aliases"].append(text)

            # Update canonical if new mention is longer
            if len(text) > len(self.entity_map[best_key]["canonical"]):
                self.entity_map[best_key]["canonical"] = text
                self.embeddings[best_key] = new_emb
            return best_key

        # --- Create new entity ---
        entity_uuid = uuid.uuid4().hex[:4]
        new_key = f"{entity_type}_{entity_uuid}"
        self.entity_map[new_key] = {"canonical": text, "aliases": [text]}
        self.embeddings[new_key] = new_emb
        return new_key

    def de_anonymise_text(self, text):
        # Replace keys with canonical entity names
        for key, data in self.entity_map.items():
            pattern = r"\b" + re.escape(key) + r"\b"
            text = re.sub(pattern, data["canonical"], text)
        return text
