#!/usr/bin/env python3
"""TemperFM

Usage:
  temperfm weekly <username> <weeks> [--config=<path>]
  temperfm (-h | --help)
  temperfm --version

Options:

  --config=<path>  Config file to use
  -h, --help       Show this screen
  --version        Show version
"""

import os
import sys


sys.path.remove(os.path.dirname(__file__))


def main():
    from docopt import docopt
    from temperfm import __version__, config

    args = docopt(__doc__, version=f'TemperFM {__version__}')

    try:
        config.load(args['--config'])

        if args['weekly']:
            from temperfm import get_user_weekly_artists

            kwargs = {}

            try:
                kwargs['limit'] = int(args['<weeks>'])
            except (TypeError, ValueError):
                pass

            report = get_user_weekly_artists(args['<username>'], **kwargs)
            print(report.to_json())
    except RuntimeError as e:
        sys.stderr.write(f'{e}\n')
        exit(1)


if __name__ == '__main__':
    main()
