import os
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from .rag_manager import RAGManager

MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise ValueError("MODEL_PATH environment variable is not set")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = LlamaTokenizer.from_pretrained(MODEL_PATH)
model = LlamaForCausalLM.from_pretrained(MODEL_PATH, device_map="auto")

# Initialize RAG
# Assuming running from root, so dataset/ds.json is correct.
print("Initializing RAG System...")
rag = RAGManager(dataset_path="dataset/ds.json")

def task_extractor(log):
    # Try RAG first
    rag_action = rag.get_action(log, score_threshold=0.8) # Stricter threshold for accuracy
    if rag_action:
        print(f"RAG Action Found: {rag_action}")
        if "no error" in rag_action.lower():
            return None
        return rag_action

    print("RAG found no match, falling back to LLM...")
    
    prompt = (
    "Instruction: Identify if there is any error in the given log. "
    "If there is error, provide the action to resolve the error.\n"
    f"Input: ${log}.\n"
    "Output:")

    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
        # do_sample=False is better for deterministic output
        do_sample=False
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Output:" in result:
        result = result.split("Output:")[-1].strip()
    result = result.replace("</s>", "").strip()

    print("Task Extracted: ", result, "\n")
    if result:
         if "no error" in result.lower():
             return None
         else:
             return result
    return None
