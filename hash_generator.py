
#!/usr/bin/env python3
import os
import sys
import hashlib
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial

# Попытка импортировать tqdm для прогресс-бара
try:
    from tqdm import tqdm
except ImportError:
    print("Ошибка: не найдена библиотека tqdm. Установите её командой:\n    pip3 install tqdm", file=sys.stderr)
    sys.exit(1)

def find_dat_files(root):
    """Генератор путей ко всем *.dat (без .shm и .wal) в дереве root."""
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".dat") and not (fname.endswith(".dat-shm") or fname.endswith(".dat-wal")):
                yield os.path.join(dirpath, fname)

def hash_file(path, root):
    """Вычислить SHA256-файл и вернуть (хеш, относительный путь)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    rel = os.path.relpath(path, root)
    return h.hexdigest(), rel

def main():
    parser = argparse.ArgumentParser(description="Вычисление SHA256 для всех .dat-файлов")
    parser.add_argument("root", help="Корневая папка (например, /data/blocks)")
    parser.add_argument("output", help="Файл для записи результатов")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(),
                        help="Число параллельных процессов (по умолчанию – все CPU)")
    args = parser.parse_args()

    # Собираем список файлов (несколько тысяч — быстро)
    files = list(find_dat_files(args.root))
    total = len(files)
    if total == 0:
        print(f"Не найдено .dat-файлов в {args.root}", file=sys.stderr)
        sys.exit(1)

    # Параллельная обработка с прогресс-баром
    with Pool(processes=args.workers) as pool, open(args.output, "w") as out, \
         tqdm(total=total, unit="file", desc="Хеширование") as pbar:
        for digest, relpath in pool.imap_unordered(partial(hash_file, root=args.root), files):
            out.write(f"{digest}  {relpath}\n")
            pbar.update()

    print(f"Готово! Всего файлов: {total}. Результаты в {args.output}")

if __name__ == "__main__":
    main()
