#!/usr/bin/env python3
"""
BIP-39 Mnemonic Generator & Validator
Образовательный инструмент для понимания структуры seed-фраз.
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
    from mnemonic import Mnemonic
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
    """Возвращает баланс в USD (пример через BlockCypher, курс BTC/USD)."""
    try:
        # Получаем баланс в сатоши
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        balance_sat = data.get("balance", 0)
        btc = balance_sat / 1e8

        # Получаем курс BTC/USD (Coingecko)
        price_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        price_resp = requests.get(price_url, timeout=5)
        btc_usd = price_resp.json().get("bitcoin", {}).get("usd", 0)
        return btc * btc_usd
    except Exception as e:
        print(f"  Ошибка проверки баланса: {e}")
        return 0.0

# Пример интеграции в меню (добавить пункт 8)
def check_balance_of_mnemonic():
    phrase = input("  Введите seed фразу (12 слов): ").strip()
    if not is_valid_mnemonic(phrase):
        print("  ❌ Невалидная фраза")
        return
    addr = get_btc_address_from_mnemonic(phrase)
    usd = check_btc_balance(addr)
    print(f"\n  Адрес: {addr}")
    print(f"  Баланс: {usd:.2f} USD")
    if usd >= 1.0:
        print("  ✅ Кошелёк имеет ≥ 1 USD")
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
    entropy = secrets.token_bytes(16)  # 16 bytes = 128 bits
    return entropy_to_mnemonic(entropy)


# ─── Как работает checksum BIP-39 ─────────────────────────────────────────

def explain_checksum(mnemonic_phrase: str) -> None:
    """Показывает, как устроена контрольная сумма в фразе."""
    mnemo = Mnemonic("english")
    words = mnemonic_phrase.strip().split()

    if len(words) != 12:
        print("  ⚠ Работает только с 12-словными фразами")
        return

    # Каждый слово → 11-битный индекс
    wordlist = mnemo.wordlist
    indices = [wordlist.index(w) for w in words]

    # Собираем 132 бита (128 entropy + 4 checksum)
    bits = ""
    for idx in indices:
        bits += format(idx, "011b")

    entropy_bits = bits[:128]
    checksum_bits = bits[128:]

    # Пересчитываем checksum
    entropy_bytes = int(entropy_bits, 2).to_bytes(16, "big")
    hash_hex = hashlib.sha256(entropy_bytes).hexdigest()
    expected_checksum = format(int(hash_hex, 16), "0256b")[:4]

    valid = checksum_bits == expected_checksum

    print(f"  Entropy (128 бит):  {entropy_bits}")
    print(f"  Checksum (4 бит):   {checksum_bits}")
    print(f"  Ожидаемый checksum: {expected_checksum}")
    print(f"  Валидность:         {'✅ Валидна' if valid else '❌ Невалидна'}")


# ─── Генерация с поиском по паттерну ──────────────────────────────────────

def search_mnemonic_with_pattern(
    pattern: str,
    position: int = 0,
    max_attempts: int = 1_000_000
) -> Optional[str]:
    """
    Генерирует валидные фразы, пытаясь найти слово, содержащее `pattern`
    на позиции `position` (0-11). Демонстрация — не для реального поиска.
    """
    if not (0 <= position <= 11):
        print("  ⚠ position должна быть от 0 до 11")
        return None

    print(f"  Поиск фразы со словом '~{pattern}~' на позиции {position}")
    print(f"  Лимит попыток: {max_attempts:,}")
    print()

    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist

    # Фильтруем слова, содержащие паттерн
    matching_words = [w for w in wordlist if pattern.lower() in w.lower()]
    if not matching_words:
        print(f"  ⚠ Нет слов, содержащих '{pattern}'")
        return None

    print(f"  Найдено слов с паттерном: {len(matching_words)}")
    print(f"  Примеры: {matching_words[:5]}")
    print()

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

    elapsed = time.time() - start
    print(f"  ❌ Не найдено за {attempts:,} попыток ({elapsed:.2f}с)")
    return None


# ─── Восстановление при известных 11 из 12 слов ──────────────────────────

def recover_missing_word(
    partial_words: List[str],
    missing_index: int
) -> List[str]:
    """
    Если известны 11 из 12 слов, находит все возможные варианты
    12-го слова, при которых фраза валидна.
    """
    if len(partial_words) != 12:
        print("  ⚠ Нужно ровно 12 слов (одно — placeholder '?')")
        return []

    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    valid_phrases = []

    print(f"  Перебор слова на позиции {missing_index}...")
    print(f"  Пространство: {len(wordlist)} слов")
    print()

    for candidate in wordlist:
        test_words = partial_words.copy()
        test_words[missing_index] = candidate
        phrase = " ".join(test_words)

        if mnemo.check(phrase):
            valid_phrases.append(phrase)
            print(f"  ✅ Валидна: ... {candidate} ...")

    print(f"\n  Итого валидных вариантов: {len(valid_phrases)}")
    return valid_phrases


# ─── Массовая генерация и валидация ───────────────────────────────────────

def batch_generate_and_validate(count: int = 100_000) -> None:
    """
    Генерирует N случайных фраз и проверяет их.
    Демонстрирует, что все сгенерированные через to_mnemonic() валидны.
    """
    mnemo = Mnemonic("english")
    valid = 0
    invalid = 0

    print(f"  Генерация {count:,} случайных фраз...\n")
    start = time.time()

    for i in range(count):
        entropy = secrets.token_bytes(16)
        phrase = mnemo.to_mnemonic(entropy)

        if mnemo.check(phrase):
            valid += 1
        else:
            invalid += 1

        if (i + 1) % 25_000 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  ... {i+1:,} / {count:,} ({rate:,.0f} фраз/сек)")

    elapsed = time.time() - start
    print(f"\n  Результат:")
    print(f"    Валидных:   {valid:,}")
    print(f"    Невалидных: {invalid:,}")
    print(f"    Время:      {elapsed:.2f}с")
    print(f"    Скорость:   {count/elapsed:,.0f} фраз/сек")


# ─── Проверка случайных комбинаций (brute-force demo) ────────────────────

def random_combination_check(max_attempts: int = 1_000_000) -> None:
    """
    Случайно выбирает 12 слов из wordlist (без расчёта checksum)
    и проверяет, окажется ли фраза валидной.
    Демонстрирует, что вероятность ≈ 1/16 (4 бита checksum).
    """
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    wordlist_len = len(wordlist)  # 2048

    valid_count = 0
    print(f"  Случайный подбор {max_attempts:,} комбинаций...")
    print(f"  Ожидаемая валидность: ~1/16 ≈ {max_attempts/16:,.0f}\n")

    start = time.time()

    for i in range(max_attempts):
        # Случайные 12 слов (без учёта checksum)
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
    print(f"\n  Результат:")
    print(f"    Валидных: {valid_count} / {max_attempts:,}")
    print(f"    Соотношение: {ratio:.6f} (≈ 1/{1/ratio:.1f})")
    print(f"    Время: {elapsed:.2f}с")


# ─── Интерактивное меню ──────────────────────────────────────────────────

def print_menu():
    print("\n" + "=" * 60)
    print("  BIP-39 Mnemonic Tool")
    print("=" * 60)
    print("  1. Сгенерировать случайную валидную фразу")
    print("  2. Проверить свою фразу на валидность")
    print("  3. Разобрать checksum фразы")
    print("  4. Поиск фразы с паттерном в слове")
    print("  5. Восстановить 12-е слово (известны 11)")
    print("  6. Массовая генерация и валидация")
    print("  7. Случайный подбор (демо checksum)")
    print("  0. Выход")
    print("=" * 60)


def main():
    while True:
        print_menu()
        choice = input("\n  Выбор: ").strip()

        if choice == "1":
            count = int(input("  Сколько фраз? [1]: ") or "1")
            for i in range(count):
                phrase = generate_random_mnemonic()
                print(f"\n  [{i+1}] {phrase}")
                print(f"      Валидна: {is_valid_mnemonic(phrase)}")

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
            if len(words) != 12:
                print("  ⚠ Нужно ровно 12 слов")
                continue
            if "?" not in words:
                print("  ⚠ Нет placeholder '?'")
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

        elif choice == "0":
            print("\n  Bye! 👋")
            sys.exit(0)

        else:
            print("  ⚠ Неверный выбор")


if __name__ == "__main__":
    main()