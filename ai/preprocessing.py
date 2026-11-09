import re


def clean_text(text: str) -> str:
    """
    Membersihkan teks sebelum diberikan ke model.
    """

    if not isinstance(text, str):
        raise TypeError("Input harus berupa string.")

    # Menghapus spasi berlebih
    text = re.sub(r"\s+", " ", text)

    # Menghapus spasi di awal dan akhir
    text = text.strip()

    return text