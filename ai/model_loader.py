import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from ai.model_config import MODEL_PATHS, load_label_config


# Menentukan perangkat yang digunakan
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# Cache model yang sudah dimuat
MODEL_CACHE = {}


def load_model(task_name: str):
    """
    Memuat tokenizer dan model IndoBERT
    berdasarkan nama task.
    """

    # Gunakan model dari cache jika sudah pernah dimuat
    if task_name in MODEL_CACHE:
        return MODEL_CACHE[task_name]

    if task_name not in MODEL_PATHS:
        raise ValueError(f"Task tidak dikenal: {task_name}")

    model_path = MODEL_PATHS[task_name]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Folder model tidak ditemukan: {model_path}"
        )

    # Membaca konfigurasi model
    config = load_label_config(task_name)

    # Memuat tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path)
    )

    # Memuat model hasil training
    model = AutoModelForSequenceClassification.from_pretrained(
        str(model_path)
    )

    # Memastikan jumlah label sesuai konfigurasi
    if model.config.num_labels != len(config["labels"]):
        raise ValueError(
            f"Jumlah output model {task_name} "
            f"({model.config.num_labels}) tidak sesuai "
            f"dengan jumlah labels di label_config.json "
            f"({len(config['labels'])})."
        )

    model.to(DEVICE)
    model.eval()

    # Simpan ke cache
    MODEL_CACHE[task_name] = {
        "model": model,
        "tokenizer": tokenizer,
        "config": config
    }

    print(f"Model {task_name} berhasil dimuat.")

    return MODEL_CACHE[task_name]


def load_all_models():
    """
    Memuat seluruh model SafeSpace.
    """

    loaded_models = {}

    for task_name in MODEL_PATHS:
        loaded_models[task_name] = load_model(task_name)

    return loaded_models