from pathlib import Path
import json

# Lokasi folder ai/
AI_DIR = Path(__file__).resolve().parent

# Lokasi penyimpanan model
MODEL_DIR = AI_DIR / "saved_model"

# Nama folder masing-masing model
MODEL_PATHS = {
    "ai1_deteksi": MODEL_DIR / "model_ai1_deteksi",
    "ai2_kategori": MODEL_DIR / "model_ai2_kategori",
    "ai2_level": MODEL_DIR / "model_ai2_level",
}


def load_label_config(task_name: str) -> dict:
    """
    Membaca label_config.json milik model tertentu.
    """

    if task_name not in MODEL_PATHS:
        raise ValueError(f"Task tidak dikenal: {task_name}")

    config_path = MODEL_PATHS[task_name] / "label_config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"File konfigurasi tidak ditemukan: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = ["labels", "mode"]

    for key in required_keys:
        if key not in config:
            raise ValueError(
                f"Konfigurasi {task_name} tidak memiliki key '{key}'"
            )

    if config["mode"] not in ["multilabel", "single-label", "single"]:
        raise ValueError(
            f"Mode model {task_name} tidak dikenali: {config['mode']}"
        )

    return config


def get_all_model_configs() -> dict:
    """
    Membaca konfigurasi semua model.
    """

    return {
        task_name: load_label_config(task_name)
        for task_name in MODEL_PATHS
    }