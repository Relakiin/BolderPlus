import requests

GITLAB_PROJECT_ID = '68606627'

def get_latest_release():
    url = f'https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/releases'
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()
    return releases[0] if releases else None

def download_asset(asset_url, output_path):
    response = requests.get(asset_url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)