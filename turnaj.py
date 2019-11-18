"""Piškvorkový turnaj

Tento program otestuje strategie, které jsou v adresáři "strategie".
Soubory se strategiemi by se měly jmenovat podle autorky, např "petra.py"

Potřebné knihovny se dají doinstalovat pomocí:

    pip install pytest blessings
"""

# Tento program používá spoustu nových či složitých věcí.
# Začněme knihovnami:

import sys
import pkgutil
import time
import collections
import importlib
import argparse 

import blessings
import pytest

import strategie

# Načteme argumenty příkazové řádky, které ovlivňují chování programu.
# Zadáním `python turnaj.py --help` se ukáže nápověda.

parser = argparse.ArgumentParser()
parser.add_argument("-n", dest="num", type=int, default=1, metavar="NUM",
                    help="Počet kol turnaje (1)")
parser.add_argument("-s", dest="num_shown", type=int, default=1, metavar="NUM",
                    help="Počet kol s detailním výpisem (1)")
parser.add_argument("-w", dest="wait", action="store_true",
                    help="V klíčových bodech čekat na stisknutí <Enter>")
parser.add_argument("-p", dest="len_pole", type=int, default=20,
                    help="Dálka pole")
parser.add_argument(dest="module_names", metavar="AI_MODULE", nargs='*',
                    help="AI moduly, které se mají použít; "
                    "pokud žádné nejsou zadány, ppoužijí se všechny.")

opts = parser.parse_args()

#
# Import testů
#

import test_ai

# Z modulu test_ai vezmeme všechny proměnné, jejichž jméno začíná na "test_"
# (a budeme doufat že to jsou funkce)
tests = [t for n, t in vars(test_ai).items() if n.startswith('test_')]
# Seznam testů seřadíme podle čísla řádku, kde funkce začíná
tests.sort(key=lambda t: t.__code__.co_firstlineno)

#
# Import strategií
#

# Pomocí knihovny "pkgutil" se dají načíst všechny moduly z "strategie", i když
# předem nevíme které to jsou.
# Pokud uživatel zadal moduly na příkazové řádce, vyfiltrujeme je tady.
ais = []
ai_names = set()
modules_iter = pkgutil.iter_modules(strategie.__path__)
for i, (finder, name, ispkg) in enumerate(modules_iter):
    if (not opts.module_names) or (name in opts.module_names):
        ai_names.add(name)
        ai = finder.find_module(name).load_module(name)
        ais.append(ai)
        ai.index = i

# Kontrola, že uživatel nezadal moduly, které se výše nenačetly.
not_found_names = set(opts.module_names) - ai_names
if opts.module_names and not_found_names:
    parser.error('modul nenalezen: {}'.format(', '.join(not_found_names)))

#
# Funkce na omezení doby běhu programu
#

def call_with_watchdog(func, *args, **kwargs):
    """Zavolá danou funkci; vyvolá výjimku pokud volání trvá příliš dlouho

    Např. místo:
        print(1, 2, 3, sep=', ')
    zavolej:
        call_with_watchdog(print, 1, 2, 3, sep=', ')

    Vyhodnocování argumentů se nepočítá do doby strávené funkcí.
    (Na některé operace tato funkce nefunguje; je použitelná proti
    nechtěným nekonečným cyklům, ne proti "nepřátelskému" kódu.)
    """
    # Funkce `sys.settrace` umožní zavolat funkci po provedení každého řádku
    # kódu. My po každém řádku zkontrolujeme, že nebyl překročen časový limit.
    # Pozor – pokud `sys.settrace` už nastavil někdo jinak, tato funkce
    # nastavení přepíše. Proto by se podobná "magie" neměla moc používat,
    # zvláště ne v knihovnách.
    start = time.perf_counter()
    limit = 0.1
    line_count = 0
    def tracer(frame, event, arg):
        nonlocal line_count
        if event == 'line':
            line_count += 1
        elapsed = time.perf_counter() - start
        if elapsed > limit:
            msg = 'Volání funkce trvá příliš dlouho ({0:.3} s, {1} řádků)'
            raise Timeout(msg.format(elapsed, line_count))
        return tracer
    sys.settrace(tracer)
    try:
        return func(*args, **kwargs)
    finally:
        sys.settrace(None)

class Timeout(Exception):
    """Výjimka, kterou používá funkce call_with_watchdog"""

#
# Paranoidní volání funkce tah_pocitace
#

def check_ai_call(func, pole, symbol):
    """Zavolá danou funkci typu tah_pocitace a zkontroluje, že se zachovala správně

    Funkce musí vrátit správně dllouhý řetězec, ve kterém je právě jedno '-'
    změněno na `symbol`.
    """
    before = pole
    after = call_with_watchdog(func, pole, symbol)
    assert isinstance(after, str), "Funkce nevrátila řetězec: {0!r}".format(after)
    assert len(before) == len(after), "Funkce vrátila špatně dlouhý řetězec: {0!r}".format(after)
    diff = [(a, b) for a, b in zip(before, after) if a != b]
    assert diff == [('-', symbol)], 'Špatný stav: {}'.format(after)
    return after


def wait():
    """Pokud bylo nastaveno čekání (přepínač -w na přík.ř.), počká na stisk Enter
    """
    if opts.wait:
        input()

# Objekt "Terminal" nám umožní např. vypisovat barevný text
term = blessings.Terminal()


def hr(symbol='=', color=term.green):
    """Vypíše oddělovací řádku skládající se z daných symbolů"""
    print(color(symbol * (term.width or 79)))

def highlight(before, after):
    """Vrátí hrací pole s barevně zvýrazněnými změnami

    Změny proti předchozí verzi pole se vypíšou zeleně.
    Pokud někdo vyhrál, je výherní trojice zvýrazněna (tučně).
    """
    pole = after
    end = None
    result = []
    for i, (b, a) in enumerate(zip(before, after)):
        if i == end:
            result.append(term.normal)
            end = None
        if after[i:i+3] in ('ooo', 'xxx'):
            result.append(term.bold)
            end = i + 3
        if a == b:
            result.append(a)
        else:
            result.append(term.green(a))
            if end:
                result.append(term.bold)
    if end:
        result.append(term.normal)
    return ''.join(result)

#
# Výpis účastnic
#

hr()
print('Účastnice:')
for ai in ais:
    print('    {}'.format(ai.__name__))

wait()

#
# Puštění testů
#

hr()
print('Testy:')


# Hlavička tabulky
for i, test in enumerate(tests):
    print('    {}: {}'.format(i, test.__doc__.strip().partition('\n')[0]))


# Tělo tabulky
print()
print('{0:>20} {1}'.format('', ' '.join(str(i) for i in range(len(tests)))))
error_info = []
for ai in ais:
    results = []
    for i, test in enumerate(tests):
        try:
            call_with_watchdog(test, ai)
        except AssertionError as e:
            result = 'F'
            error_info.append((ai, i, test, e))
        except Timeout as e:
            result = 'T'
            error_info.append((ai, i, test, e))
        except BaseException as e:
            result = 'E'
            error_info.append((ai, i, test, e))
        else:
            result = '.'
        results.append(result)
    result_reprs = {
        'E': term.red('E'),
        'F': term.red('F'),
        'T': term.red('T'),
        '.': term.green('.'),
    }
    print('{0:>20} {1}'.format(ai.__name__,
                              ' '.join(result_reprs.get(r,r) for r in results)))

wait()

# Výpis jednotlivých chyb
hr('-', term.blue)
for ai, i, test, e in error_info:
    print('{ai}[{i}]: {tp}{e}'.format(
        ai=ai.__name__,
        i=i,
        tp=term.red(type(e).__name__),
        e=(': ' + str(e).strip().partition('\n')[0]) if str(e) else ''
    ))

wait()

#
# Samotný turnaj
#

# Výsledky budeme ukládat do slovníku, který přiřadí dvojicím strategií
# dosažené body.
# Speciální slovník "defaultdict" umí to, že hodnoty zatím neexistujících
# klíčů se nastaví na 0.
results = collections.defaultdict(float)

if opts.num:
    hr()
    print('Turnáááj!')

for cislo_turnaje in range(opts.num):
    hr('-', term.blue)
    # Detailní výpisy chceme jen u prvních P turnajů.
    # Uděláme si funkci, která buď bude print, nebo nebude dělat nic.
    if cislo_turnaje < opts.num_shown:
        write = print
    else:
        def write(*a, **ka):
            """Nedělá nic"""
            return

    for a in ais:
        for b in ais:
            write()
            if cislo_turnaje < opts.num_shown:
                wait()
            write('{a} (x) vs. {b} (o)'.format(a=a.__name__, b=b.__name__))
            pole = before = '-' * opts.len_pole
            cislo_tahu = 0
            while True:
                write('    {0:4} {1}'.format(cislo_tahu,
                                             highlight(before, pole)))
                if opts.wait and cislo_turnaje < opts.num_shown:
                    time.sleep(.01)
                if 'xxx' in pole:
                    write('    {} vyhrála; +1 bod'.format(a.__name__))
                    results[a, b] += 1
                    break
                elif 'ooo' in pole:
                    write('    {} vyhrála; +1 bod'.format(b.__name__))
                    results[b, a] += 1
                    break
                elif '-' not in pole:
                    write('    Remíza; půl bodu oběma'.format(b.__name__))
                    results[a, b] += 0.5
                    results[b, a] += 0.5
                    break
                before = pole
                try:
                    if cislo_tahu % 2 == 0:
                        ai = a
                        other = b
                        symbol = 'x'
                    else:
                        ai = b
                        other = a
                        symbol = 'o'
                    pole = check_ai_call(ai.tah_pocitace, pole, symbol)
                except Exception as e:
                    write('    {}: {}'.format(term.red(type(e).__name__), e))
                    write('    {} vyhrála; +1 bod'.format(other.__name__))
                    results[other, ai] += 1
                    write('    {} vyvolala chybu; -1 bod'.format(ai.__name__))
                    results[ai, other] -= 1
                    break
                cislo_tahu += 1

    # Vytvořit seznam strategií seřazený podle pořadí
    # (strategie, které nastavují DQ=True, se neumisťují)
    ai_scores = collections.defaultdict(float)
    for (a, b), n in results.items():
        ai_scores[a] += n
    ai_scores = [k for i, (k, v)
                 in enumerate(sorted(ai_scores.items(),
                                     key=lambda k_v: -k_v[1]))
                 if not getattr(k, 'DQ', False)]

    # Výpis tabulky turnaje
    print()
    print('Pořadí po {0}. kole turnaje'.format(cislo_turnaje + 1))

    print('{0:>10}  '.format(''), end='')
    for b in ais:
        print('{0:>5.5} '.format(b.__name__), end='')
    print(' Celkem')
    for a in ais:
        print('{0:>10}: '.format(a.__name__), end='')
        total = 0
        for b in ais:
            print('{0:5} '.format(results[a, b]), end='')
            total += results[a, b]
        try:
            rank = ai_scores.index(a)
        except ValueError:
            print('{0:7.7}    DQ'.format(total))
        else:
            if rank == 0:
                trophy = term.yellow('\N{TROPHY}')
            elif rank == 1:
                trophy = term.white('\N{SECOND PLACE MEDAL}')
            elif rank == 2:
                trophy = term.red('\N{THIRD PLACE MEDAL}')
            else:
                trophy = '  '
            print('{0:7.7} {t} {1}. místo'.format(total, rank+1, t=trophy))

    if cislo_turnaje < opts.num_shown:
        wait()
