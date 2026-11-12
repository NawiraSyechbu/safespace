
import sys
from pathlib import Path

# Menambahkan folder utama proyek ke Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from ai.moderation_engine import analyze_text


def display_result(result: dict):
    """
    Menampilkan hasil analisis ketiga model.
    """

    print("\n" + "=" * 55)
    print("HASIL ANALISIS SAFESPACE")
    print("=" * 55)

    print("\nTeks:", result["text"])
    print("Status:", result["status"])

    for task_name, prediction in result["predictions"].items():

        if prediction is None:
            print(f"\nMODEL: {task_name} -> tidak dijalankan (HS tidak terdeteksi)")
            continue

        print("\n" + "-" * 45)
        print(f"MODEL: {task_name}")
        print("-" * 45)

        print("Mode:", prediction["mode"])

        if prediction["mode"] == "multilabel":

            print(
                "Predicted labels:",
                prediction["predicted_labels"]
            )

            print("\nThreshold:")
            for label, threshold in prediction["thresholds"].items():
                print(f"  {label}: {threshold:.4f}")

        else:

            print(
                "Predicted label:",
                prediction["predicted_label"]
            )

            print(
                "Confidence:",
                f"{prediction['confidence']:.4f}"
            )

        print("\nScores:")

        for label, score in prediction["scores"].items():
            print(f"  {label}: {score:.4f}")

    print("\n" + "=" * 55)


if __name__ == "__main__":

    sample_text = (
        "Saya senang bisa berdiskusi dan berbagi "
        "pendapat dengan teman-teman di komunitas ini."
    )

    try:

        print("Memulai analisis teks...")

        result = analyze_text(sample_text)

        display_result(result)

        print("\nPengujian AI berhasil diselesaikan.")

    except Exception as error:

        print("\nTerjadi kesalahan saat menjalankan model:")
        print(type(error).__name__, ":", error)
