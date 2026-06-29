"""Helper to PUT artifact bytes given a JSON payload from prepare_artifact_uploads.

Usage:
  python3 .upload_helper.py <batch_json_file> <png_path> <svg_path>

Where <batch_json_file> contains the full batch JSON response (paste it).
"""
import sys, json, urllib.request


def put_file(url, headers, file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(url, data=data, method='PUT', headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status


def main():
    batch = json.load(open(sys.argv[1]))['batch']
    files = sys.argv[2:]
    for item, f in zip(batch['items'], files):
        code = put_file(item['upload_url'], item['headers'], f)
        print(f"{f} -> {code}")
    print("batch_token:", batch['batch_token'])


if __name__ == '__main__':
    main()
