
import sys
from pathlib import Path

# Menambahkan folder utama proyek ke Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from ai.moderation_engine import (
    analyze_text,
    determine_moderation
)


def test_moderation_rules():

    print("\n========== TEST ATURAN MODERASI ==========")

    # ----------------------------------
    # TEST 1: TIDAK ADA DETEKSI HS
    # ----------------------------------

    result = determine_moderation(
        detection_result={
            "predicted_labels": []
        }
    )

    assert result["status"] == "approved"

    print("Test 1 berhasil: Konten tanpa deteksi HS/Abusive.")

    # ----------------------------------
    # TEST 2: ABUSIVE TANPA HS
    # ----------------------------------

    result = determine_moderation(
        detection_result={
            "predicted_labels": ["Abusive"]
        }
    )

    assert result["status"] == "pending_review"

    print("Test 2 berhasil: Abusive tanpa HS.")

    # ----------------------------------
    # TEST 3: HS WEAK
    # ----------------------------------

    result = determine_moderation(
        detection_result={
            "predicted_labels": ["HS"]
        },
        category_result={
            "predicted_labels": ["HS_Individual"]
        },
        level_result={
            "predicted_label": "HS_Weak"
        }
    )

    assert result["status"] == "pending_review"

    print("Test 3 berhasil: HS_Weak.")

    # ----------------------------------
    # TEST 4: HS MODERATE
    # ----------------------------------

    result = determine_moderation(
        detection_result={
            "predicted_labels": ["HS"]
        },
        category_result={
            "predicted_labels": ["HS_Group"]
        },
        level_result={
            "predicted_label": "HS_Moderate"
        }
    )

    assert result["status"] == "pending_review"

    print("Test 4 berhasil: HS_Moderate.")

    # ----------------------------------
    # TEST 5: HS STRONG
    # ----------------------------------

    result = determine_moderation(
        detection_result={
            "predicted_labels": ["HS"]
        },
        category_result={
            "predicted_labels": ["HS_Religion"]
        },
        level_result={
            "predicted_label": "HS_Strong"
        }
    )

    assert result["status"] == "blocked"

    print("Test 5 berhasil: HS_Strong.")

    print("\nSemua pengujian aturan moderasi berhasil!")


def test_real_model():

    print("\n========== TEST MODEL INDO BERT ==========")

    sample_text = (
        "Saya senang bisa berdiskusi dan berbagi "
        "pendapat dengan teman-teman di komunitas ini."
    )

    result = analyze_text(sample_text)

    print("\nTeks:", result["text"])
    print("Status:", result["status"])
    print("Decision:", result["decision"])
    print("Reason:", result["reason"])

    if result["predictions"] is not None:

        for task_name, prediction in result["predictions"].items():

            print(f"\n--- {task_name} ---")

            if prediction is None:
                print("Tidak dijalankan.")
                continue

            print("Mode:", prediction["mode"])

            if prediction["mode"] == "multilabel":
                print(
                    "Predicted labels:",
                    prediction["predicted_labels"]
                )
            else:
                print(
                    "Predicted label:",
                    prediction["predicted_label"]
                )
                print(
                    "Confidence:",
                    prediction["confidence"]
                )


if __name__ == "__main__":

    test_moderation_rules()
    test_real_model()
