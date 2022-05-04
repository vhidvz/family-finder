"""
# python pkglunch.py --site locatefamily.com -name=&Clark -phone=|440000000 location=UK
"""
import sys
import json
import argparse

from websites import getPersonsByLocateFamily

lookup = {
    'locatefamily.com': getPersonsByLocateFamily,
}


def main(site, args):

    kwargs = dict([(key, value)
                   for key, value in vars(args).items() if not value == None])

    if 'string' in kwargs:
        kyval = kwargs['string'].split('&')
        for item in kyval:
            kwargs.update([item.split(':')])

    for key, value in kwargs.items():
        if '+' in value:
            kwargs[key] = kwargs[key].replace('+', ' ')
        if "'" in value or '"' in value:
            kwargs[key] = kwargs[key].replace('"', '')
            kwargs[key] = kwargs[key].replace("'", '')

    if site == None:
        results = []
        for url, fcn in lookup.items():
            status, data = fcn(**kwargs)
            results.append({'site': url, 'fetched': {
                           'status': status, 'data': data}})
        print(json.dumps(results))
    elif site in lookup:
        status, data = lookup[site](**kwargs)
        print(json.dumps({'site': site, 'status': status, 'data': data}))
    else:
        print(json.dumps({'status': 404}))


parser = argparse.ArgumentParser(
    description="Helping you find your loved ones! Over 350 million people from around the world!")
parser.add_argument(
    "--site", help="The site you want to fetch data from it (all|name of site).",
    type=str, default=None, nargs='?')
with open('./websites/Info.json') as f:
    support = json.load(f)['_support']
    for item in support.split('|')[:-1]:
        parser.add_argument(
            '-'+item, help="Find people by {}.".format(item),
            type=str, default=None, nargs='?')
parser.add_argument(
    '-string', help="Example: address:UK&location:Leeds",
    type=str, default=None, nargs='?')

args = parser.parse_args()
site = args.site
del args.site
main(site, args)
