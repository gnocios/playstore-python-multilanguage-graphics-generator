import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "output"
DESTINO = BASE / "por_idioma"

CARPETAS = [
    "banner_img",
    "store_img_01",
    "store_img_02",
    "store_img_03",
    "store_img_04",
    "store_img_05",
    "store_img_06",
    "store_img_07",
    "store_img_08",
]


def main():
    copiadas = 0

    for nombre in CARPETAS:
        carpeta = BASE / nombre
        if not carpeta.is_dir():
            print(f"[AVISO] No existe la carpeta: {carpeta}")
            continue

        for archivo in sorted(carpeta.glob("*.png")):
            # El idioma es lo que va después del último "_" y antes de ".png"
            idioma = archivo.stem.rsplit("_", 1)[-1]

            carpeta_idioma = DESTINO / idioma
            carpeta_idioma.mkdir(parents=True, exist_ok=True)

            shutil.copy2(archivo, carpeta_idioma / archivo.name)
            copiadas += 1

    print(f"Listo: {copiadas} imágenes copiadas en {DESTINO}")


if __name__ == "__main__":
    main()