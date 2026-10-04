"""Download an IDC (NCI Imaging Data Commons, AWS open data) DICOM series over HTTPS."""
import concurrent.futures
import os
import re
import subprocess
import sys

from idc_index import IDCClient


def fetch(uid, out):
    df = IDCClient().index
    row = df[df.SeriesInstanceUID == uid].iloc[0]
    prefix = row.series_aws_url.replace('s3://idc-open-data/', '').rstrip('*')
    os.makedirs(out, exist_ok=True)
    keys, token = [], None
    while True:
        url = f'https://s3.amazonaws.com/idc-open-data?list-type=2&prefix={prefix}'
        if token:
            import urllib.parse
            url += '&continuation-token=' + urllib.parse.quote(token)
        x = subprocess.run(['curl', '-sS', url], capture_output=True, text=True).stdout
        keys += re.findall(r'<Key>([^<]+)</Key>', x)
        m = re.search(r'<NextContinuationToken>([^<]+)</NextContinuationToken>', x)
        if not m:
            break
        token = m.group(1)

    def get(k):
        p = os.path.join(out, k.split('/')[-1])
        if not os.path.exists(p):
            subprocess.run(['curl', '-sS', '-o', p, 'https://s3.amazonaws.com/idc-open-data/' + k])
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        list(ex.map(get, keys))
    return row, len(keys)


if __name__ == '__main__':
    for uid, name in zip(sys.argv[1::2], sys.argv[2::2]):
        row, n = fetch(uid, name)
        print(name, n, row.collection_id, row.source_DOI, row.license_short_name)
