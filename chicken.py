# 🐔 1. Install dependencies (run in Colab or your environment)
# !pip install transformers datasets accelerate

from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset, Dataset
import torch

# 🐔 2. Load pre-trained TinyLlama for chat
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 🐔 3. Prepare your chicken joke dataset
# Example jokes, replace with your larger dataset for real training
data = {
    "prompt": [
        "Tell me a chicken joke.",
        "Give me a funny chicken joke.",
        "I need a chicken joke, please."
    ],
    "completion": [
        "Why did the chicken join a band? Because it had the drumsticks!",
        "Why did the chicken sit in the middle of the road? It wanted to lay it on the line!",
        "Why did the chicken cross the playground? To get to the other slide!"
    ]
}

# Create Hugging Face dataset
dataset = Dataset.from_dict(data)
dataset = dataset.train_test_split(test_size=0.2)

# 🐔 4. Tokenization
def tokenize_function(examples):
    full_text = [p + " " + c for p, c in zip(examples["prompt"], examples["completion"])]
    return tokenizer(full_text, truncation=True, padding="max_length", max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets = tokenized_datasets.remove_columns(["prompt", "completion"])

# 🐔 5. Training Arguments
training_args = TrainingArguments(
    output_dir="./chicken_joke_llm",
    evaluation_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    fp16=True,
    save_total_limit=1,
    logging_steps=10,
    report_to="none"
)

# 🐔 6. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
)

# 🐔 7. Train
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./chicken_joke_llm")
tokenizer.save_pretrained("./chicken_joke_llm")

print("🎉 Model fine-tuned and saved successfully!")

# 🐔 8. Generate Chicken Jokes interactively
from transformers import pipeline

pipe = pipeline("text-generation", model="./chicken_joke_llm", tokenizer="./chicken_joke_llm")

# Generate 3 chicken jokes
prompts = [
    "Tell me a chicken joke.",
    "Write a funny chicken joke for kids.",
    "Give me a new chicken crossing the road joke."
]

for prompt in prompts:
    result = pipe(prompt, max_length=50, num_return_sequences=1, do_sample=True, top_p=0.9)[0]['generated_text']
    print(f"\n🐔 Prompt: {prompt}\n😂 Joke: {result}\n")
