import os
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer

MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise ValueError("MODEL_PATH environment variable is not set")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = LlamaTokenizer.from_pretrained(MODEL_PATH)

model = LlamaForCausalLM.from_pretrained(MODEL_PATH, device_map="auto")

def task_extractor(log):
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
        do_sample=False
    )


    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Output:" in result:
        result = result.split("Output:")[-1].strip()
    result = result.replace("</s>", "").strip()

    print("\nTask Extracted:\n", result)
    return result if "No error detected" not in result else None
