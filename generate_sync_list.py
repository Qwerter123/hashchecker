#!/usr/bin/env python3
import argparse

def load_hashes(path):
    d = {}
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue
            h, rel = parts
            d[rel] = h
    return d

def main():
    p = argparse.ArgumentParser(
        description="Генерация списка файлов для rsync (недостающие и битые)")
    p.add_argument('donor',   help='Файл хешей донора')
    p.add_argument('local',   help='Файл локальных хешей')
    p.add_argument('-o','--output', default='to_sync.txt',
                   help='Куда записать список (default: to_sync.txt)')
    args = p.parse_args()

    h_donor = load_hashes(args.donor)
    h_local = load_hashes(args.local)

    set_d = set(h_donor)
    set_l = set(h_local)

    # файлы, которых нет у вас
    only_d = sorted(set_d - set_l)
    # файлы есть у обоих, но хеши не совпали
    mismatched = sorted([f for f in set_d & set_l if h_donor[f] != h_local[f]])

    to_sync = only_d + mismatched

    with open(args.output, 'w') as out:
        for rel in to_sync:
            out.write(rel + "\n")

    print(f"Список для rsync ({len(to_sync)}): {args.output}")

if __name__ == "__main__":
    main()
