#!/usr/bin/env python3

import re
import sys


def main():
    assert '.html' in sys.argv[1]

    with open(sys.argv[1]) as fp:
        html = fp.read()

    html = html.replace(
        '<body id="preview"',
        '\n<body id="preview" style="max-width:760px;font-size:1.1em;"')

    found = re.findall(r'<li><a href="#(_\d+)">(.+)</a>', html, re.UNICODE)

    for k, v in found:

        p = r'<a id=".+"></a>{}'.format(v)
        r = r'<a name="{}"></a>{}'.format(k, v)

        if not re.search(p, html):
            print(k, v, "NOT FOUND")
            continue

        html = re.sub(p, r, html)

    with open(sys.argv[1], 'w') as fp:
        fp.write(html)


if __name__ == '__main__':
    main()
