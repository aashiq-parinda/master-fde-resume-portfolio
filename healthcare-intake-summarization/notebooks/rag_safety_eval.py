# %% [markdown]
# # Patient Intake Summarization - RAG & Safety Evaluation Pipeline
# 
# This interactive notebook/script outlines the training, embedding creation, and offline evaluation
# pipeline for the clinical pre-visit summarizer and diagnostic containment filter.
# All code is documented and commented out for reference/mock deployment.

# %%
# # 1. SETUP AND DEPENDENCIES
# # In a live GPU environment, you would run:
# # !pip install sentence-transformers transformers torch pandas scikit-learn pgvector

# import os
# import json
# import torch
# import pandas as pd
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# %% [markdown]
# # 2. CLINICAL GUIDELINES CORPUS & VECTOR EMBEDDINGS
# # Here we simulate embedding the clinical guidelines corpus and storing them in pgvector.

# %%
# # Initialize local embedding model
# # embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Sample guidelines corpus
# # guidelines_data = [
# #     {"category": "Chest Pain", "text": "Refer to cardiac facility. Check ECG.", "flags": "jaw pain, arm numbness, sweating"},
# #     {"category": "Dyspnea", "text": "Oxygen support. Check O2 sats.", "flags": "accessory muscle use, stridor, cyanosis"},
# #     {"category": "Abdominal Pain", "text": "Evaluate surgical abdomen. Keep NPO.", "flags": "rebound tenderness, rigid abdomen"}
# # ]

# # df_guidelines = pd.DataFrame(guidelines_data)

# # Create embeddings
# # print("Computing vector embeddings for guidelines...")
# # df_guidelines["embedding"] = df_guidelines.apply(
# #     lambda row: embed_model.encode(f"{row['category']} - {row['flags']} - {row['text']}").tolist(),
# #     axis=1
# # )
# # print("Embeddings successfully calculated.")

# %% [markdown]
# # 3. RETRIEVAL (RAG) SIMULATION
# # Matching patient inputs to clinical guidelines using vector cosine similarity.

# %%
# # def retrieve_guideline_rag(query, df, embed_model, top_k=1):
# #     query_vector = embed_model.encode(query)
# #     
# #     # Compute cosine similarities
# #     similarities = []
# #     for idx, row in df.iterrows():
# #         vec = np.array(row["embedding"])
# #         sim = np.dot(query_vector, vec) / (np.linalg.norm(query_vector) * np.linalg.norm(vec))
# #         similarities.append((sim, row))
# #         
# #     similarities.sort(key=lambda x: x[0], reverse=True)
# #     return [item[1] for item in similarities[:top_k]]

# # Test Query
# # query = "I have pressure on my chest and severe pain running down my left arm"
# # matched = retrieve_guideline_rag(query, df_guidelines, embed_model)
# # print("Matched Guideline Category:", matched[0]["category"])

# %% [markdown]
# # 4. LLM GENERATION & POST-GENERATION SAFETY GATE
# # Orchestrates generation and checks for diagnostic term leakages.

# %%
# # Initialize LLM (e.g. Llama-3-8B-Instruct or Mistral-7B-Instruct)
# # model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
# # tokenizer = AutoTokenizer.from_pretrained(model_id)
# # llm_pipeline = pipeline("text-generation", model=model_id, tokenizer=tokenizer, device_map="auto")

# # Programmatic Blacklist
# # blacklist = ["appendicitis", "migraine", "bronchitis", "stroke", "sepsis", "heart attack"]

# # def run_safety_filter(text):
# #     words = set(text.lower().split())
# #     violations = [w for w in words if w in blacklist]
# #     return len(violations) == 0, violations

# # def generate_summary_with_gate(patient_text, guidelines_context):
# #     prompt = f"Summarize symptoms descriptively. NEVER output a diagnosis.\nGuidelines:\n{guidelines_context}\nPatient:\n{patient_text}"
# #     
# #     attempts = 0
# #     max_attempts = 3
# #     while attempts < max_attempts:
# #         attempts += 1
# #         outputs = llm_pipeline(prompt, max_new_tokens=256)
# #         generated_text = outputs[0]["generated_text"]
# #         
# #         is_safe, terms = run_safety_filter(generated_text)
# #         if is_safe:
# #             return generated_text, attempts
# #         else:
# #             print(f"Attempt {attempts} blocked! Contained diagnostic leakage: {terms}")
# #             prompt += f"\nWarning: Do not use the terms {terms}. Rewrite without diagnosing."
# #             
# #     # Fallback
# #     return "Safety block fallback: descriptive symptom logging initiated.", attempts

# # summary, attempts_count = generate_summary_with_gate(query, matched[0]["text"])
# # print(f"Final safe summary (generated in {attempts_count} attempts):\n{summary}")
