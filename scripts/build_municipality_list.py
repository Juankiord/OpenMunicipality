"""Builds data/conprel/all_municipalities.csv.gz: every Spanish municipality with its INE
code, so the app can tell apart "not in the Ministry's database" from "does
not exist".

Default source: Code for Spain's dataset (public domain, ODC-PDDL), which
mirrors the INE municipal code list (relation at 1 January 2026 at the time of
writing). Any CSV with the columns municipio_id and nombre can be passed with
--source.

    python scripts/build_municipality_list.py
"""
import argparse
import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ('https://raw.githubusercontent.com/codeforspain/'
           'ds-organizacion-administrativa/master/data/municipios.csv')


def _readable_name():
    spec = importlib.util.spec_from_file_location(
        'build_conprel', ROOT / 'scripts' / 'build_conprel.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.readable_name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--source', default=DEFAULT)
    args = parser.parse_args()
    readable = _readable_name()
    raw = pd.read_csv(args.source, dtype=str)
    out = pd.DataFrame({'ine_code': raw['municipio_id'].str.zfill(5),
                        'name': raw['nombre'].map(readable)})
    path = ROOT / 'data' / 'conprel' / 'all_municipalities.csv.gz'
    out.sort_values('ine_code').to_csv(path, index=False)
    print(f'{len(out)} municipalities written to {path}')


if __name__ == '__main__':
    main()
