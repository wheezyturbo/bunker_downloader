import os
import requests
from bs4 import BeautifulSoup
import sys
import urllib.parse
from tqdm import tqdm

def download_media(url, download_folder):
    # Create the download folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Send an HTTP GET request and parse the HTML content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all anchor elements with an "href" attribute
    anchor_elements = soup.find_all('a', href=True)

    for anchor in anchor_elements:
        href = anchor['href']
        # Check if the link points to a page containing media files
        if not href.endswith('.mp4'):
            continue

        linked_page_url = urllib.parse.urljoin(url, href)
        
        # Send an HTTP GET request to the linked page
        try:
            linked_page_response = requests.get(linked_page_url)
            linked_page_response.raise_for_status()  # Check for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch linked page URL: {e}")
            continue

        linked_soup = BeautifulSoup(linked_page_response.text, 'html.parser')

        # Find all anchor elements with an "href" attribute in the linked page
        linked_anchor_elements = linked_soup.find_all('a', href=True)

        for linked_anchor in linked_anchor_elements:
            linked_href = linked_anchor['href']
            # Check if the link points to a media file (you may need to refine this check)
            if linked_href.endswith(('.jpg', '.png', '.gif', '.jpeg', '.mp4', '.avi', '.mkv', '.mov')):
                media_url = urllib.parse.urljoin(linked_page_url, linked_href)
                # Extract the media file name from the URL
                file_name = os.path.basename(media_url)

                # Check if the file already exists in the download folder
                if os.path.isfile(os.path.join(download_folder, file_name)):
                    print(f"Skipped: {file_name} (Already downloaded)")
                    continue

                # Download and save the media file with progress tracking
                try:
                    response = requests.get(media_url, stream=True)
                    response.raise_for_status()  # Check for HTTP errors
                    total_size = int(response.headers.get('content-length', 0))

                    with open(os.path.join(download_folder, file_name), 'wb') as media_file, tqdm(
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        total=total_size,
                        desc=f"Downloading {file_name}",
                    ) as progress_bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            media_file.write(chunk)
                            progress_bar.update(len(chunk))
                    
                    print(f"Downloaded: {file_name}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download {file_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] == '--help':
        print("Usage: python download_media.py <webpage_url> <download_folder>")
        sys.exit(1)

    webpage_url = sys.argv[1]
    download_folder = sys.argv[2]

    download_media(webpage_url, download_folder)

