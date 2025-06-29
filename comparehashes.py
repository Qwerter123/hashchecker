#!/usr/bin/env python3
"""
compare_hashes.py: сравнение хешей с анализом позиции и цветной ASCII-графикой:
- Красным: количество битых (.не совпавших) блоков в корзине
- Зеленым: количество правильных (совпавших)
- Пропорциональные бары по максимальному объему

Usage:
  python3 compare_hashes.py hashes1.txt hashes2.txt [--output report.txt]
                           [--threshold-blocks N] [--plot] [--bins M]
"""
import argparse
import sys
import os

# Цвета для консоли
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_OK = Fore.GREEN
    COLOR_FAIL = Fore.RED
    COLOR_INFO = Fore.CYAN
    COLOR_RESET = Style.RESET_ALL
except ImportError:
    COLOR_OK = COLOR_FAIL = COLOR_INFO = COLOR_RESET = ''

def load_hashes(path):
    hashes = {}
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue
            h, rel = parts
            hashes[rel] = h
    return hashes

def get_file_index(relpath):
    try:
        return int(os.path.splitext(os.path.basename(relpath))[0])
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Сравнение хешей с ASCII-гистограммой')
    parser.add_argument('file1', help='Эталонный файл хешей')
    parser.add_argument('file2', help='Проверяемый файл хешей')
    parser.add_argument('-o', '--output', help='Файл для подробного отчёта')
    parser.add_argument('--threshold-blocks', type=int, default=20000,
                        help='Порог последних блоков как не критичных')
    parser.add_argument('--plot', action='store_true', help='Построить и показать гистограмму')
    parser.add_argument('--bins', type=int, default=50, help='Число корзин для гистограммы')
    args = parser.parse_args()

    # Загрузка хешей
    h1 = load_hashes(args.file1)
    h2 = load_hashes(args.file2)
    paths1, paths2 = set(h1), set(h2)
    common = paths1 & paths2

    # Списки индексов
    diffs = sorted([p for p in common if h1[p] != h2[p]], key=lambda p: get_file_index(p) or 0)
    diff_idxs = [get_file_index(p) for p in diffs if get_file_index(p) is not None]
    match_idxs = [get_file_index(p) for p in common if p not in diffs and get_file_index(p) is not None]

    only1 = sorted(paths1 - paths2)
    only2 = sorted(paths2 - paths1)

    # Статистика
    total1 = len(paths1)
    total2 = len(paths2)
    total_common = len(common)
    total_diffs = len(diff_idxs)
    matched = total_common - total_diffs

    # Краткий отчёт
    print(f"{COLOR_INFO}Краткий отчёт:{COLOR_RESET}")
    if match_idxs:
        print(f"{COLOR_OK}Совпало: {matched} [{min(match_idxs)}–{max(match_idxs)}]{COLOR_RESET}")
    else:
        print(f"{COLOR_OK}Совпало: {matched}{COLOR_RESET}")
    if diff_idxs:
        print(f"{COLOR_FAIL}Не совпало: {total_diffs} [{min(diff_idxs)}–{max(diff_idxs)}]{COLOR_RESET}")
    else:
        print(f"{COLOR_FAIL}Не совпало: {total_diffs}{COLOR_RESET}")
    print()

    # Подробный отчёт
    lines = [
        f"Всего эталон: {total1}",
        f"Всего провер: {total2}",
        f"Общие: {total_common}",
        f"Только эталон: {len(only1)}", f"Только провер: {len(only2)}",
        f"Несовпали: {total_diffs}",
    ]
    if args.threshold_blocks and diff_idxs and min(diff_idxs) >= max(diff_idxs) - args.threshold_blocks + 1:
        lines.append(f"Все отличия в последних ~{args.threshold_blocks} блоках — не критично.")
    lines.append("")
    if only1:
        lines.append("Только в эталоне:")
        lines.extend(only1)
        lines.append("")
    if only2:
        lines.append("Только в проверяемом:")
        lines.extend(only2)
        lines.append("")
    if diffs:
        lines.append("Различаются файлы:")
        for p in diffs:
            lines.append(f"{p}\n  {args.file1}: {h1[p]}\n  {args.file2}: {h2[p]}")
        lines.append("")

    # Сохраняем отчёт
    out = open(args.output, 'w') if args.output else sys.stdout
    for ln in lines:
        print(ln, file=out)
    if args.output:
        out.close()
        print(f"Подробный отчёт: {args.output}")

    # ASCII-гистограмма с двумя цветами
    if args.plot:
        if not diff_idxs and not match_idxs:
            print("Нет данных для гистограммы.")
            return
        print("ASCII-гистограмма распределения:")
        all_idx = diff_idxs + match_idxs
        base, top = min(all_idx), max(all_idx)
        span = top - base + 1
        bins = args.bins
        size = max(1, span // bins)
        # Считаем
        bad_counts = [0]*bins
        good_counts = [0]*bins
        for i in diff_idxs:
            idx = min((i-base)//size, bins-1)
            bad_counts[idx] += 1
        for i in match_idxs:
            idx = min((i-base)//size, bins-1)
            good_counts[idx] += 1
        # Нормализация
        max_total = max((good_counts[i]+bad_counts[i]) for i in range(bins))
        width = 40
        for j in range(bins):
            start = base + j*size
            end = start + size - 1
            good = good_counts[j]
            bad = bad_counts[j]
            total = good + bad
            bar_len = int((total/max_total)*width) if max_total>0 else 0
            if total>0:
                good_len = int((good/total)*bar_len)
                bad_len = bar_len - good_len
            else:
                good_len = bad_len = 0
            bar = COLOR_OK + '█'*good_len + COLOR_FAIL + '█'*bad_len + COLOR_RESET
            print(f"{start:>6}-{end:<6} | {bar} ({good}/{bad})")

if __name__ == '__main__':
    main()
