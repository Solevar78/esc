#!/usr/bin/env python3
"""
BIP-39 Mnemonic Generator & Validator
Образовательный инструмент для понимания структуры seed-фраз.
С добавлением поиска кошельков с балансом ≥ $1
"""

import os
import sys
import time
import hashlib
import secrets
from typing import List, Optional, Tuple
from mnemonic import Mnemonic
import requests
from bip32utils import BIP32Key


def get_btc_address_from_mnemonic(mnemonic: str, index: int = 0) -> str:
    """Генерирует BTC адрес (BIP44) для первой пары ключей."""
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(mnemonic)  # bytes
    # BIP44 для Bitcoin: m/44'/0'/0'/0/index
    master_key = BIP32Key.fromEntropy(seed)
    purpose = master_key.ChildKey(44 + 0x80000000)   # 44'
    coin_type = purpose.ChildKey(0 + 0x80000000)     # 0'
    account = coin_type.ChildKey(0 + 0x80000000)     # 0'
    external = account.ChildKey(0)
    address_key = external.ChildKey(index)
    return address_key.Address()


def check_btc_balance(address: str) -> float:
    """Возвращает баланс в USD."""
    try:
        # Получаем баланс в сатоши
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        resp = requests.get(url, timeout=8)
        data = resp.json()
        balance_sat = data.get("balance", 0)
        btc = balance_sat / 1e8

        # Получаем курс BTC/USD
        price_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        price_resp = requests.get(price_url, timeout=8)
        btc_usd = price_resp.json().get("bitcoin", {}).get("usd", 0)
        
        usd_balance = btc * btc_usd
        return round(usd_balance, 2)
    except Exception as e:
        # print(f"  Ошибка проверки баланса: {e}")  # закомментировано для скорости
        return 0.0


def check_balance_of_mnemonic():
    """Проверка одной конкретной фразы."""
    phrase = input("  Введите seed фразу (12 слов): ").strip()
    if not is_valid_mnemonic(phrase):
        print("  ❌ Невалидная фраза")
        return
    addr = get_btc_address_from_mnemonic(phrase)
    usd = check_btc_balance(addr)
    print(f"\n  Адрес: {addr}")
    print(f"  Баланс: {usd:.2f} USD")
    if usd >= 1.0:
        print("  ✅ Кошелёк имеет ≥ 1 USD!")
    else:
        print("  ❌ Меньше 1 USD")


# ─── Утилиты ───────────────────────────────────────────────────────────────

def entropy_to_mnemonic(entropy: bytes) -> str:
    """Конвертирует байты энтропии в BIP-39 мнемоническую фразу."""
    mnemo = Mnemonic("english")
    return mnemo.to_mnemonic(entropy)


def is_valid_mnemonic(mnemonic_phrase: str) -> bool:
    """Проверяет валидность BIP-39 фразы (включая checksum)."""
    mnemo = Mnemonic("english")
    return mnemo.check(mnemonic_phrase)


def generate_random_mnemonic() -> str:
    """Генерирует случайную валидную 12-словную фразу (128 бит энтропии)."""
    entropy = secrets.token_bytes(16)
    return entropy_to_mnemonic(entropy)


# ─── Поиск кошельков с балансом ≥ $1 ──────────────────────────────────────

def hunt_funded_wallets(max_attempts: int = 1_000_000, save_to_file: bool = True):
    """
    Брутфорс-поиск seed-фраз с балансом ≥ 1 USD.
    Работает очень медленно (вероятность крайне мала), но демонстрирует принцип.
    """
    print(f"  Запуск поиска кошельков с балансом ≥ $1")
    print(f"  Максимум попыток: {max_attempts:,}")
    print(f"  Результаты будут сохраняться в found_wallets.txt\n")

    mnemo = Mnemonic("english")
    found = 0
    start_time = time.time()
    filename = "found_wallets.txt"

    try:
        for attempt in range(1, max_attempts + 1):
            phrase = generate_random_mnemonic()
            address = get_btc_address_from_mnemonic(phrase)
            balance_usd = check_btc_balance(address)

            if balance_usd >= 1.0:
                found += 1
                elapsed = time.time() - start_time
                print(f"\n{'='*70}")
                print(f"  🎉 НАЙДЕН КОШЕЛЁК С БАЛАНСОМ!")
                print(f"  Попытка: {attempt:,}")
                print(f"  Фраза: {phrase}")
                print(f"  Адрес: {address}")
                print(f"  Баланс: {balance_usd:.2f} USD")
                print(f"  Время: {elapsed:.1f} сек")
                print(f"{'='*70}\n")

                if save_to_file:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(f"{'='*60}\n")
                        f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Фраза: {phrase}\n")
                        f.write(f"Адрес: {address}\n")
                        f.write(f"Баланс: {balance_usd:.2f} USD\n")
                        f.write(f"Попытка: {attempt}\n\n")

            if attempt % 5000 == 0:
                elapsed = time.time() - start_time
                speed = attempt / elapsed if elapsed > 0 else 0
                print(f"  [{attempt:>8,}] попыток | скорость: {speed:,.0f} фраз/сек | найдено: {found}", end="\r")

    except KeyboardInterrupt:
        print("\n\n  Поиск остановлен пользователем.")

    finally:
        total_time = time.time() - start_time
        print(f"\n\n  Поиск завершён.")
        print(f"  Всего попыток: {attempt:,}")
        print(f"  Найдено кошельков: {found}")
        print(f"  Общее время: {total_time:.1f} секунд")


# ─── Остальные функции (checksum, recover и т.д.) ─────────────────────────

def explain_checksum(mnemonic_phrase: str) -> None:
    """Показывает, как устроена контрольная сумма в фразе."""
    mnemo = Mnemonic("english")
    words = mnemonic_phrase.strip().split()

    if len(words) != 12:
        print("  ⚠ Работает только с 12-словными фразами")
        return

    wordlist = mnemo.wordlist
    indices = [wordlist.index(w) for w in words]

    bits = ""
    for idx in indices:
        bits += format(idx, "011b")

    entropy_bits = bits[:128]
    checksum_bits = bits[128:]

    entropy_bytes = int(entropy_bits, 2).to_bytes(16, "big")
    hash_hex = hashlib.sha256(entropy_bytes).hexdigest()
    expected_checksum = format(int(hash_hex, 16), "0256b")[:4]

    valid = checksum_bits == expected_checksum

    print(f"  Entropy (128 бит):  {entropy_bits}")
    print(f"  Checksum (4 бит):   {checksum_bits}")
    print(f"  Ожидаемый checksum: {expected_checksum}")
    print(f"  Валидность:         {'✅ Валидна' if valid else '❌ Невалидна'}")


def search_mnemonic_with_pattern(
    pattern: str,
    position: int = 0,
    max_attempts: int = 1_000_000
) -> Optional[str]:
    if not (0 <= position <= 11):
        print("  ⚠ position должна быть от 0 до 11")
        return None

    print(f"  Поиск фразы со словом '~{pattern}~' на позиции {position}")
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    matching_words = [w for w in wordlist if pattern.lower() in w.lower()]
    
    if not matching_words:
        print(f"  ⚠ Нет слов, содержащих '{pattern}'")
        return None

    attempts = 0
    start = time.time()

    for _ in range(max_attempts):
        attempts += 1
        entropy = secrets.token_bytes(16)
        phrase = mnemo.to_mnemonic(entropy)
        words = phrase.split()

        if pattern.lower() in words[position].lower():
            elapsed = time.time() - start
            print(f"  ✅ Найдено за {attempts:,} попыток ({elapsed:.2f}с)")
            print(f"  Фраза: {phrase}")
            return phrase

        if attempts % 100_000 == 0:
            elapsed = time.time() - start
            rate = attempts / elapsed if elapsed > 0 else 0
            print(f"  ... {attempts:,} попыток ({rate:,.0f}/сек)")

    print(f"  ❌ Не найдено за {attempts:,} попыток")
    return None


def recover_missing_word(
    partial_words: List[str],
    missing_index: int
) -> List[str]:
    if len(partial_words) != 12:
        print("  ⚠ Нужно ровно 12 слов (одно — placeholder '?')")
        return []

    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    valid_phrases = []

    print(f"  Перебор слова на позиции {missing_index}...")

    for candidate in wordlist:
        test_words = partial_words.copy()
        test_words[missing_index] = candidate
        phrase = " ".join(test_words)

        if mnemo.check(phrase):
            valid_phrases.append(phrase)
            print(f"  ✅ Валидна: ... {candidate} ...")

    print(f"\n  Итого валидных вариантов: {len(valid_phrases)}")
    return valid_phrases


def batch_generate_and_validate(count: int = 100_000) -> None:
    mnemo = Mnemonic("english")
    valid = 0
    start = time.time()

    for i in range(count):
        entropy = secrets.token_bytes(16)
        phrase = mnemo.to_mnemonic(entropy)
        if mnemo.check(phrase):
            valid += 1

        if (i + 1) % 25_000 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  ... {i+1:,} / {count:,} ({rate:,.0f} фраз/сек)")

    elapsed = time.time() - start
    print(f"\n  Валидных: {valid:,} / {count:,}")
    print(f"  Время: {elapsed:.2f}с")


def random_combination_check(max_attempts: int = 1_000_000) -> None:
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    wordlist_len = len(wordlist)
    valid_count = 0
    start = time.time()

    for i in range(max_attempts):
        words = [wordlist[secrets.randbelow(wordlist_len)] for _ in range(12)]
        phrase = " ".join(words)

        if mnemo.check(phrase):
            valid_count += 1

        if (i + 1) % 250_000 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  ... {i+1:,} проверено, валидных: {valid_count} ({rate:,.0f}/сек)")

    elapsed = time.time() - start
    ratio = valid_count / max_attempts if max_attempts > 0 else 0
    print(f"\n  Валидных: {valid_count} / {max_attempts:,} ≈ {ratio:.6f} (1/{1/ratio:.1f})")


# ─── Интерактивное меню ──────────────────────────────────────────────────

def print_menu():
    print("\n" + "=" * 70)
    print("          BIP-39 Mnemonic Tool + Balance Hunter")
    print("=" * 70)
    print("  1. Сгенерировать случайную валидную фразу")
    print("  2. Проверить свою фразу на валидность")
    print("  3. Разобрать checksum фразы")
    print("  4. Поиск фразы с паттерном в слове")
    print("  5. Восстановить 12-е слово (известны 11)")
    print("  6. Массовая генерация и валидация")
    print("  7. Случайный подбор (демо checksum)")
    print("  8. 🔥 Поиск кошельков с балансом ≥ $1 (Balance Hunter)")
    print("  9. Проверить баланс одной фразы")
    print("  0. Выход")
    print("=" * 70)


def main():
    print("BIP-39 Tool запущен. Для поиска реальных балансов требуется очень много времени.")
    while True:
        print_menu()
        choice = input("\n  Выбор: ").strip()

        if choice == "1":
            count = int(input("  Сколько фраз? [1]: ") or "1")
            for i in range(count):
                phrase = generate_random_mnemonic()
                print(f"\n  [{i+1}] {phrase}")

        elif choice == "2":
            phrase = input("  Введите 12 слов через пробел:\n  > ").strip()
            valid = is_valid_mnemonic(phrase)
            print(f"\n  {'✅ Валидна' if valid else '❌ Невалидна'}")

        elif choice == "3":
            phrase = input("  Введите фразу:\n  > ").strip()
            print()
            explain_checksum(phrase)

        elif choice == "4":
            pattern = input("  Паттерн для поиска: ").strip()
            pos = int(input("  Позиция (0-11) [0]: ") or "0")
            max_att = int(input("  Макс. попыток [1000000]: ") or "1000000")
            print()
            search_mnemonic_with_pattern(pattern, pos, max_att)

        elif choice == "5":
            print("  Введите 12 слов, заменив неизвестное на '?'")
            phrase = input("  > ").strip()
            words = phrase.split()
            if len(words) != 12 or "?" not in words:
                print("  ⚠ Нужно ровно 12 слов с одним '?'")
                continue
            missing_idx = words.index("?")
            print()
            recover_missing_word(words, missing_idx)

        elif choice == "6":
            count = int(input("  Сколько фраз? [100000]: ") or "100000")
            print()
            batch_generate_and_validate(count)

        elif choice == "7":
            count = int(input("  Сколько попыток? [1000000]: ") or "1000000")
            print()
            random_combination_check(count)

        elif choice == "8":
            attempts = int(input("  Максимум попыток [500000]: ") or "500000")
            print()
            hunt_funded_wallets(max_attempts=attempts)

        elif choice == "9":
            check_balance_of_mnemonic()

        elif choice == "0":
            print("\n  Bye! 👋")
            sys.exit(0)

        else:
            print("  ⚠ Неверный выбор")


if __name__ == "__main__":
    main()
