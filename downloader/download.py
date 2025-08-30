import requests
import os
import concurrent.futures
from .scraper import get_chapter_images
from .utils import create_chapter_directory
from config import DOWNLOAD_PATH, MAX_IMAGE_THREADS, MAX_CHAPTER_THREADS

import time

def download_image(img_url, img_path, session):
    """Downloads a single image with a retry mechanism."""
    retries = 3
    for attempt in range(retries):
        try:
            with session.get(img_url, stream=True) as response:
                response.raise_for_status()
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            return f"Downloaded {img_path}"
        except requests.exceptions.RequestException as e:
            print(f"  Error downloading {img_url}: {e}. Retrying ({attempt+1}/{retries})...")
            time.sleep(2)  # Wait 2 seconds before retrying
    return f"Failed to download {img_url} after {retries} attempts."

def download_chapter_images(manga_title, chapter):
    """
    Downloads all images for a single chapter concurrently.
    """
    chapter_number = chapter['number']
    chapter_url = chapter['url']
    print(f"Downloading Chapter {chapter_number}...")

    image_urls = get_chapter_images(chapter_url)
    if not image_urls:
        print(f"Could not retrieve images for Chapter {chapter_number}.")
        return

    chapter_path = create_chapter_directory(DOWNLOAD_PATH, manga_title, chapter_number)
    
    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_IMAGE_THREADS) as executor:
            futures = []
            for i, img_url in enumerate(image_urls):
                img_name = f"{i+1:03d}.jpg"
                img_path = os.path.join(chapter_path, img_name)
                futures.append(executor.submit(download_image, img_url, img_path, session))
            
            for future in concurrent.futures.as_completed(futures):
                print(f"  {future.result()}")

    print(f"Chapter {chapter_number} download complete.")

def download_chapters_concurrently(manga_title, chapters):
    """
    Downloads multiple chapters concurrently.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CHAPTER_THREADS) as executor:
        futures = {executor.submit(download_chapter_images, manga_title, chapter): chapter for chapter in chapters}
        for future in concurrent.futures.as_completed(futures):
            chapter = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Chapter {chapter['number']} generated an exception: {e}")