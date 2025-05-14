from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
from huggingface_hub import login
import os
from dotenv import load_dotenv

load_dotenv()

login(token=os.getenv('TOKEN'))

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b')
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b')

train_data = load_dataset('json', data_files='../../data/train.json')
test_data = load_dataset('json', data_files='../../data/test.json')

def tokenize(example):
    tokenized = tokenizer(
        example["prompt"] + "\n" + example["completion"],
        truncation=True,
        padding="max_length",
        max_length=1024,
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

train_data = train_data.map(tokenize, batched=True)
test_data = test_data.map(tokenize, batched=True)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

args = TrainingArguments(
    output_dir='./results/fine_tuned_model',
    evaluation_strategy='epoch',
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_steps=10,
    fp16=True,
    max_grad_norm=1.0,
    load_best_model_at_end=True,
    save_steps=500,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_data,
    eval_dataset=test_data,
    tokenizer=tokenizer,
    data_collator=data_collator
)

trainer.train()
results = trainer.evaluate()
print(results)

trainer.save_model('./results/fine_tuned_model')
tokenizer.save_pretrained('./results/fine_tuned_model')
