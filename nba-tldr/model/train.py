import torch
from datasets import load_dataset
from transformers import TrainingArguments, DataCollatorForLanguageModeling, Trainer
from unsloth import FastLanguageModel

MODEL_NAME = "unsloth/llama-2-7b-bnb-4bit"  # 4-bit LLaMA 2

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    use_cache=False,
    device_map="auto",
    dtype=torch.float16,
    load_in_4bit=True,
    attn_implementation="eager"
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
)

train_dataset = load_dataset('json', data_files='../../data/train.jsonl')['train']
eval_dataset = load_dataset('json', data_files='../../data/test.jsonl')['train']

def format_example(example):
    return {
        "text": f"<s>[INST] {example['info']} [/INST] {example['summary']} </s>"
    }

train_dataset = train_dataset.map(format_example)
eval_dataset = eval_dataset.map(format_example)

# print(train_dataset[0])

def tokenize(example):
    encoded = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=2048,
        return_tensors="pt"
    )
    
    input_ids = encoded["input_ids"][0]
    attention_mask = encoded["attention_mask"][0]
    
    end_inst_token_id = tokenizer.convert_tokens_to_ids("[/INST]")
    
    try:
        matches = (input_ids == end_inst_token_id).nonzero(as_tuple=True)[0]
        sep_index = matches[0].item() if len(matches) > 0 else 0
    except IndexError:
        sep_index = 0
    
    labels = input_ids.clone()
    labels[:sep_index + 1] = -100
    
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }

train_dataset = train_dataset.map(tokenize, remove_columns=train_dataset.column_names)
eval_dataset = eval_dataset.map(tokenize, remove_columns=eval_dataset.column_names)

training_args = TrainingArguments(
    output_dir="nba-tldr-model",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    warmup_steps=50,
    logging_steps=10,
    save_strategy="epoch",
    learning_rate=2e-5,
    bf16=True,
    logging_dir="./logs",
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, 
    mlm=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
)
train_output = trainer.train()
print(train_output)

results = trainer.evaluate()
print(results)

model.save_pretrained("nba-tldr-model")
tokenizer.save_pretrained("nba-tldr-model")