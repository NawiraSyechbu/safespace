import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.predictor import predict

print("Ketik kalimat uji. Kosongkan lalu Enter untuk keluar.")

while True:
    text = input("\nTeks: ").strip()
    if not text:
        break

    result = predict("ai2_level", text)

    print("Label akhir:", result["predicted_label"])
    for label, score in result["scores"].items():
        print(f"  {label}: {score:.4f}")