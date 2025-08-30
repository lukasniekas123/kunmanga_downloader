import os
import re

def create_chapter_directory(base_path, manga_title, chapter_number):
    """
    Creates a directory for a specific chapter.

    Args:
        base_path (str): The root download directory.
        manga_title (str): The title of the manga.
        chapter_number (float): The chapter number.

    Returns:
        str: The path to the created directory.
    """
    manga_title = sanitize_filename(manga_title)
    chapter_dir_name = f"Chapter_{chapter_number}"
    chapter_path = os.path.join(base_path, manga_title, chapter_dir_name)
    
    os.makedirs(chapter_path, exist_ok=True)
    return chapter_path

def sanitize_filename(name):
    """
    Removes invalid characters from a string to make it a valid filename.

    Args:
        name (str): The initial filename or directory name.

    Returns:
        str: A sanitized version of the name.
    """
    # Remove invalid file system characters
    sanitized = re.sub(r'[\\/*?:"<>|]',"", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized.strip()