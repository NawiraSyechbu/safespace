
import os

from ai.predictor import predict


# ==========================================
# KONFIGURASI MODEL
# ==========================================

AI1_TASK = "ai1_deteksi"
AI2_CATEGORY_TASK = "ai2_kategori"
AI2_LEVEL_TASK = "ai2_level"


# Label dari label_config.json
HS_LABEL = "HS"
ABUSIVE_LABEL = "Abusive"

LEVEL_WEAK = "HS_Weak"
LEVEL_MODERATE = "HS_Moderate"
LEVEL_STRONG = "HS_Strong"


# ==========================================
# STATUS MODERASI
# ==========================================

STATUS_APPROVED = "approved"
STATUS_BLOCKED = "blocked"
STATUS_PENDING = "pending_review"


# ==========================================
# FUNGSI KEPUTUSAN MODERASI
# ==========================================

def determine_moderation(
    detection_result: dict,
    category_result: dict = None,
    level_result: dict = None
) -> dict:
    """
    Menentukan keputusan moderasi berdasarkan
    hasil ketiga model IndoBERT.
    """

    detected_labels = detection_result["predicted_labels"]

    is_hate_speech = HS_LABEL in detected_labels
    is_abusive = ABUSIVE_LABEL in detected_labels

    # --------------------------------------
    # KASUS 1: HS TIDAK TERDETEKSI
    # --------------------------------------

    if not is_hate_speech:

        # Abusive tanpa HS perlu diperiksa moderator
        if is_abusive:
            return {
                "status": STATUS_PENDING,
                "decision": "review",
                "reason": (
                    "Konten terdeteksi mengandung unsur abusive, "
                    "tetapi tidak terdeteksi sebagai hate speech. "
                    "Diperlukan pemeriksaan moderator."
                )
            }

        # HS dan Abusive tidak terdeteksi
        return {
            "status": STATUS_APPROVED,
            "decision": "allow",
            "reason": (
                "Konten tidak terdeteksi mengandung hate speech "
                "maupun abusive berdasarkan model AI."
            )
        }

    # --------------------------------------
    # KASUS 2: HS TERDETEKSI
    # --------------------------------------

    # Hasil kategori dan level wajib tersedia
    if category_result is None or level_result is None:
        return {
            "status": STATUS_PENDING,
            "decision": "review",
            "reason": (
                "Hate speech terdeteksi, tetapi analisis "
                "kategori atau level belum tersedia."
            )
        }

    predicted_level = level_result["predicted_label"]

    # --------------------------------------
    # KASUS 3: HATE SPEECH KUAT
    # --------------------------------------

    if predicted_level == LEVEL_STRONG:
        return {
            "status": STATUS_BLOCKED,
            "decision": "block",
            "reason": (
                "Konten terdeteksi sebagai hate speech "
                "dengan tingkat HS_Strong."
            )
        }

    # --------------------------------------
    # KASUS 4: HATE SPEECH SEDANG / LEMAH
    # --------------------------------------

    if predicted_level in [LEVEL_WEAK, LEVEL_MODERATE]:
        return {
            "status": STATUS_PENDING,
            "decision": "review",
            "reason": (
                f"Konten terdeteksi sebagai hate speech "
                f"dengan tingkat {predicted_level}. "
                "Diperlukan peninjauan moderator."
            )
        }

    # --------------------------------------
    # KASUS 5: LEVEL TIDAK DIKENALI
    # --------------------------------------

    return {
        "status": STATUS_PENDING,
        "decision": "review",
        "reason": (
            "Hate speech terdeteksi, tetapi hasil klasifikasi "
            "level tidak dikenali. Diperlukan peninjauan moderator."
        )
    }


# ==========================================
# FUNGSI UTAMA ANALISIS TEKS
# ==========================================

def analyze_text(text: str) -> dict:
    """
    Menjalankan pipeline moderasi SafeSpace.

    1. AI 1 mendeteksi HS dan Abusive.
    2. Jika HS terdeteksi, jalankan AI 2 kategori dan level.
    3. Tentukan keputusan moderasi.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Teks tidak boleh kosong.")

    # Mode uji (AI_MODE=mock di .env): hanya untuk mengetes alur web
    # tanpa file model. Jangan dipakai untuk demo/produksi.
    if os.getenv("AI_MODE", "real").lower() == "mock":
        from ai.mock_engine import mock_analyze
        return mock_analyze(text)

    try:

        # ----------------------------------
        # TAHAP 1: DETEKSI
        # ----------------------------------

        detection_result = predict(
            task_name=AI1_TASK,
            text=text
        )

        # Pastikan model AI 1 menggunakan multilabel
        if detection_result["mode"] != "multilabel":
            raise ValueError(
                "Model AI 1 harus menggunakan mode multilabel."
            )

        # ----------------------------------
        # TAHAP 2: ANALISIS LANJUTAN
        # ----------------------------------

        detected_labels = detection_result["predicted_labels"]

        category_result = None
        level_result = None

        if HS_LABEL in detected_labels:

            # AI 2 kategori
            category_result = predict(
                task_name=AI2_CATEGORY_TASK,
                text=text
            )

            # AI 2 level
            level_result = predict(
                task_name=AI2_LEVEL_TASK,
                text=text
            )

        # ----------------------------------
        # TAHAP 3: KEPUTUSAN MODERASI
        # ----------------------------------

        moderation = determine_moderation(
            detection_result=detection_result,
            category_result=category_result,
            level_result=level_result
        )

        # ----------------------------------
        # TAHAP 4: HASIL AKHIR
        # ----------------------------------

        return {
            "text": text,
            "status": moderation["status"],
            "decision": moderation["decision"],
            "reason": moderation["reason"],

            "predictions": {
                AI1_TASK: detection_result,
                AI2_CATEGORY_TASK: category_result,
                AI2_LEVEL_TASK: level_result
            }
        }

    except Exception as error:

        # Jika AI mengalami kegagalan,
        # jangan otomatis menerbitkan konten.

        return {
            "text": text,
            "status": STATUS_PENDING,
            "decision": "review",
            "reason": (
                "Analisis AI gagal dijalankan. "
                "Konten ditahan untuk pemeriksaan lebih lanjut."
            ),
            "error": str(error),
            "predictions": None
        }
