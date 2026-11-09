import torch

from ai.model_loader import load_model, DEVICE
from ai.preprocessing import clean_text


def predict(task_name: str, text: str) -> dict:
    """
    Melakukan prediksi menggunakan model tertentu.
    """

    # Membersihkan teks
    text = clean_text(text)

    if not text:
        raise ValueError("Teks tidak boleh kosong.")

    # Memuat model dan tokenizer
    components = load_model(task_name)

    model = components["model"]
    tokenizer = components["tokenizer"]
    config = components["config"]

    labels = config["labels"]
    mode = config["mode"]

    max_len = config.get("max_len", 128)

    # Tokenisasi
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=max_len
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    # Prediksi
    with torch.inference_mode():
        outputs = model(**inputs)
        logits = outputs.logits

    # Mengubah logits menjadi probabilitas
    if mode == "multilabel":
        probabilities = torch.sigmoid(logits)[0]

    elif mode in ["single-label", "single"]:
        probabilities = torch.softmax(logits, dim=-1)[0]

    else:
        raise ValueError(f"Mode tidak didukung: {mode}")

    # Mengubah hasil menjadi dictionary
    scores = {
        label: float(probabilities[index].item())
        for index, label in enumerate(labels)
    }

    # Penentuan label berdasarkan mode
    if mode == "multilabel":

        thresholds = config.get("thresholds")

        if thresholds is None:
            raise ValueError(
                f"Threshold untuk model {task_name} "
                "tidak ditemukan di label_config.json."
            )

        # Mendukung threshold berbentuk dictionary atau list
        if isinstance(thresholds, dict):
            label_thresholds = {
                label: float(thresholds[label])
                for label in labels
            }

        elif isinstance(thresholds, list):
            if len(thresholds) != len(labels):
                raise ValueError(
                    "Jumlah threshold tidak sesuai jumlah label."
                )

            label_thresholds = {
                label: float(thresholds[index])
                for index, label in enumerate(labels)
            }

        else:
            raise ValueError(
                "Format thresholds tidak didukung."
            )

        predicted_labels = [
            label
            for label in labels
            if scores[label] >= label_thresholds[label]
        ]

        result = {
            "task": task_name,
            "mode": mode,
            "predicted_labels": predicted_labels,
            "scores": scores,
            "thresholds": label_thresholds
        }

    else:

        predicted_label = max(
            scores,
            key=scores.get
        )

        result = {
            "task": task_name,
            "mode": mode,
            "predicted_label": predicted_label,
            "confidence": scores[predicted_label],
            "scores": scores
        }

    return result