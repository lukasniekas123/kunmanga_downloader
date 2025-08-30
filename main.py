import config
from downloader.scraper import get_manga_metadata
from downloader.download import download_chapters_concurrently
from downloader.converter import convert_to_pdf, convert_to_cbz

def get_chapter_selection(chapters):
    """
    Prompts the user to select chapters to download.
    """
    print("\nAvailable Chapters:")
    for i, chapter in enumerate(chapters):
        print(f"  [{i+1}] Chapter {chapter['number']}")

    while True:
        choice = input("\nEnter chapter numbers or indices to download (e.g., 5, 10-15, all): ").lower()
        selected_chapters = []
        if choice == 'all':
            return chapters
        
        try:
            for part in choice.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # Handle both by-number and by-index
                    selected_by_number = [c for c in chapters if start <= c['number'] <= end]
                    selected_by_index = chapters[start-1:end] if 1 <= start <= len(chapters) and 1 <= end <= len(chapters) else []
                    selected_chapters.extend(selected_by_number)
                    selected_chapters.extend(selected_by_index)
                else:
                    num = int(part)
                    # Handle both by-number and by-index
                    selected_by_number = [c for c in chapters if c['number'] == num]
                    selected_by_index = [chapters[num-1]] if 1 <= num <= len(chapters) else []
                    selected_chapters.extend(selected_by_number)
                    selected_chapters.extend(selected_by_index)
            
            if selected_chapters:
                # Remove duplicates and sort
                unique_chapters = {c['url']: c for c in selected_chapters}.values()
                return sorted(list(unique_chapters), key=lambda c: c['number'])
            else:
                print("No valid chapters selected. Please try again.")
        except ValueError:
            print("Invalid input. Please use the correct format (e.g., 5, 10-15, all).")

def get_conversion_options():
    """
    Prompts the user for conversion preferences.
    """
    conversion_type = input("Convert to PDF, CBZ, or None? [pdf/cbz/none]: ").lower()
    if conversion_type not in ['pdf', 'cbz']:
        conversion_type = None

    delete_choice = input("Delete original images after conversion? [y/n]: ").lower()
    if delete_choice == 'y':
        config.DELETE_IMAGES_AFTER_CONVERSION = True
    
    return conversion_type

def main():
    """
    Main function for the CLI.
    """
    print("Welcome to KunManga Downloader!")
    
    manga_url = input("Please enter the manga URL: ").strip()
    
    if not manga_url:
        print("No URL entered. Exiting.")
        return

    manga_data = get_manga_metadata(manga_url)

    if not manga_data or not manga_data['chapters']:
        print("Could not retrieve manga information. Please check the URL and website structure.")
        return

    print(f"Manga Title: {manga_data['title']}")
    print(f"Found {len(manga_data['chapters'])} chapters.")

    selected_chapters = get_chapter_selection(manga_data['chapters'])
    
    if not selected_chapters:
        print("No chapters selected. Exiting.")
        return
        
    conversion_type = get_conversion_options()

    download_chapters_concurrently(manga_data['title'], selected_chapters)

    if conversion_type:
        for chapter in selected_chapters:
            if conversion_type == 'pdf':
                convert_to_pdf(manga_data['title'], chapter['number'])
            elif conversion_type == 'cbz':
                convert_to_cbz(manga_data['title'], chapter['number'])

if __name__ == "__main__":
    main()