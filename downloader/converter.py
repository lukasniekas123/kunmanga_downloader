import os
import zipfile
from PIL import Image
from config import DELETE_IMAGES_AFTER_CONVERSION
from .utils import sanitize_filename

def convert_to_pdf(manga_title, chapter_number):
    """
    Converts a chapter's images into a single PDF file.

    Args:
        manga_title (str): The title of the manga.
        chapter_number (float): The chapter number.
    """
    chapter_path = os.path.join('./downloads', sanitize_filename(manga_title), f"Chapter_{chapter_number}")
    
    images = [img for img in sorted(os.listdir(chapter_path)) if img.endswith(".jpg")]
    if not images:
        print(f"No images found for Chapter {chapter_number} to convert to PDF.")
        return

    # Save PDF in the same folder as the images
    pdf_path = os.path.join(chapter_path, f"{sanitize_filename(manga_title)}_Chapter_{chapter_number}.pdf")
    
    pil_images = []
    for image_file in images:
        image_path = os.path.join(chapter_path, image_file)
        # Open images without converting to preserve quality
        pil_images.append(Image.open(image_path))

    if pil_images:
        # Save with original quality
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:], quality=100)
        print(f"Successfully created PDF for Chapter {chapter_number}.")
        if DELETE_IMAGES_AFTER_CONVERSION:
            cleanup_images(chapter_path, images)

def convert_to_cbz(manga_title, chapter_number):
    """
    Converts a chapter's images into a single CBZ file.

    Args:
        manga_title (str): The title of the manga.
        chapter_number (float): The chapter number.
    """
    chapter_path = os.path.join('./downloads', sanitize_filename(manga_title), f"Chapter_{chapter_number}")
    
    images = [img for img in sorted(os.listdir(chapter_path)) if img.endswith(".jpg")]
    if not images:
        print(f"No images found for Chapter {chapter_number} to convert to CBZ.")
        return

    cbz_path = os.path.join('./downloads', sanitize_filename(manga_title), f"{sanitize_filename(manga_title)}_Chapter_{chapter_number}.cbz")

    with zipfile.ZipFile(cbz_path, 'w') as cbz:
        for image_file in images:
            image_path = os.path.join(chapter_path, image_file)
            cbz.write(image_path, arcname=image_file)
    
    print(f"Successfully created CBZ for Chapter {chapter_number}.")
    if DELETE_IMAGES_AFTER_CONVERSION:
        cleanup_images(chapter_path, images)

def cleanup_images(chapter_path, image_files):
    """
    Deletes the original image files after conversion.

    Args:
        chapter_path (str): The path to the chapter's images.
        image_files (list): A list of image filenames to delete.
    """
    for image_file in image_files:
        os.remove(os.path.join(chapter_path, image_file))
    # Attempt to remove the now-empty chapter directory
    try:
        os.rmdir(chapter_path)
    except OSError:
        pass # Directory is not empty, which is unexpected but we can ignore it.
    print(f"Cleaned up images for directory {chapter_path}.")