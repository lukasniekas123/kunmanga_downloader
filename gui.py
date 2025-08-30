import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QProgressBar, QRadioButton, QCheckBox, QGroupBox, QMessageBox, QListWidgetItem
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread

from downloader.scraper import get_manga_metadata
from downloader.download import download_chapters_concurrently
from downloader.converter import convert_to_pdf, convert_to_cbz

class ScraperWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            manga_data = get_manga_metadata(self.url)
            self.finished.emit(manga_data)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)  # For progress updates

    def __init__(self, manga_title, chapters, conversion_type, delete_images):
        super().__init__()
        self.manga_title = manga_title
        self.chapters = chapters
        self.conversion_type = conversion_type
        self.delete_images = delete_images

    def run(self):
        try:
            # Download chapters
            self.progress.emit(f"Starting downloads for {len(self.chapters)} chapters...")
            download_chapters_concurrently(self.manga_title, self.chapters)
            self.progress.emit("Downloads completed.")
            
            # Convert chapters if needed
            if self.conversion_type:
                # Import config here to modify DELETE_IMAGES_AFTER_CONVERSION
                import config
                original_delete_setting = config.DELETE_IMAGES_AFTER_CONVERSION
                config.DELETE_IMAGES_AFTER_CONVERSION = self.delete_images
                
                self.progress.emit(f"Converting {len(self.chapters)} chapters to {self.conversion_type}...")
                for i, chapter in enumerate(self.chapters):
                    self.progress.emit(f"Converting chapter {chapter['number']} ({i+1}/{len(self.chapters)})...")
                    if self.conversion_type == 'pdf':
                        convert_to_pdf(self.manga_title, chapter['number'])
                    elif self.conversion_type == 'cbz':
                        convert_to_cbz(self.manga_title, chapter['number'])
                
                # Restore original setting
                config.DELETE_IMAGES_AFTER_CONVERSION = original_delete_setting
                self.progress.emit("Conversion completed.")
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class KunMangaDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KunManga Downloader")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.manga_data = None  # To store manga title and chapters

    def setup_ui(self):
        # Set dark theme
        self.set_dark_theme()

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("Manga URL:")
        self.url_input = QLineEdit()
        self.scrape_button = QPushButton("Scrape Chapters")
        self.scrape_button.clicked.connect(self.start_scraping)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.scrape_button)
        main_layout.addLayout(url_layout)

        # Chapter Selection Buttons
        selection_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_chapters)
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_chapters)
        selection_layout.addWidget(self.select_all_button)
        selection_layout.addWidget(self.deselect_all_button)
        main_layout.addLayout(selection_layout)

        # Chapter List
        self.chapter_list = QListWidget()
        self.chapter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        main_layout.addWidget(self.chapter_list)

        # Options
        options_layout = QHBoxLayout()
        
        # Conversion Options
        conversion_group = QGroupBox("Conversion Options")
        conversion_vbox = QVBoxLayout()
        self.pdf_radio = QRadioButton("PDF")
        self.cbz_radio = QRadioButton("CBZ")
        self.none_radio = QRadioButton("None")
        self.none_radio.setChecked(True)
        conversion_vbox.addWidget(self.pdf_radio)
        conversion_vbox.addWidget(self.cbz_radio)
        conversion_vbox.addWidget(self.none_radio)
        conversion_group.setLayout(conversion_vbox)
        options_layout.addWidget(conversion_group)
        
        # Cleanup Option
        self.delete_images_checkbox = QCheckBox("Delete images after conversion")
        options_layout.addWidget(self.delete_images_checkbox)

        main_layout.addLayout(options_layout)

        # Download Button
        self.download_button = QPushButton("Download Selected Chapters")
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a82da; 
                border: 1px solid white; 
            }
            QPushButton {
                border-radius: 10px;
                padding: 10px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                  stop: 0 #8A2BE2, stop: 1 #4169E1);
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                  stop: 0 #9932CC, stop: 1 #4682B4);
            }
            QLineEdit {
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #4169E1;
            }
            QListWidget {
                border-radius: 5px;
                border: 1px solid #4169E1;
            }
            QGroupBox {
                border: 1px solid #4169E1;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)

    def start_scraping(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a manga URL.")
            return

        self.scrape_button.setEnabled(False)
        self.scrape_button.setText("Scraping...")
        self.chapter_list.clear()

        self.scraper_thread = QThread()
        self.worker = ScraperWorker(url)
        self.worker.moveToThread(self.scraper_thread)

        self.scraper_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_scraping_finished)
        self.worker.error.connect(self.on_scraping_error)
        
        self.worker.finished.connect(self.scraper_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.scraper_thread.finished.connect(self.scraper_thread.deleteLater)

        self.scraper_thread.start()

    def on_scraping_finished(self, manga_data):
        self.scrape_button.setEnabled(True)
        self.scrape_button.setText("Scrape Chapters")
        if manga_data and manga_data.get('chapters'):
            self.manga_data = manga_data # Store manga data for later use
            self.setWindowTitle(f"KunManga Downloader - {manga_data['title']}")
            for chapter in manga_data['chapters']:
                self.chapter_list.addItem(f"Chapter {chapter['number']}")
        else:
            QMessageBox.information(self, "Info", "No chapters found or failed to parse manga data.")

    def on_scraping_error(self, error_message):
        self.scrape_button.setEnabled(True)
        self.scrape_button.setText("Scrape Chapters")
        QMessageBox.critical(self, "Error", f"An error occurred while scraping:\n{error_message}")

    def select_all_chapters(self):
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            if item:
                item.setSelected(True)

    def deselect_all_chapters(self):
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            if item:
                item.setSelected(False)

    def start_download(self):
        if not self.manga_data:
            QMessageBox.warning(self, "Warning", "Please scrape a manga first.")
            return
            
        # Get selected chapters
        selected_items = self.chapter_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No chapters selected for download.")
            return

        # Convert selected items to chapter objects
        selected_chapters = []
        for item in selected_items:
            chapter_text = item.text()
            # Extract chapter number from text like "Chapter 1.0"
            chapter_number = float(chapter_text.split()[-1])
            # Find the chapter object in manga_data
            for chapter in self.manga_data['chapters']:
                if chapter['number'] == chapter_number:
                    selected_chapters.append(chapter)
                    break
        
        if not selected_chapters:
            QMessageBox.warning(self, "Warning", "Could not find selected chapters.")
            return

        # Get conversion options
        conversion_type = None
        if self.pdf_radio.isChecked():
            conversion_type = 'pdf'
        elif self.cbz_radio.isChecked():
            conversion_type = 'cbz'
        
        delete_images = self.delete_images_checkbox.isChecked()

        # Disable download button and show progress
        self.download_button.setEnabled(False)
        self.download_button.setText("Downloading...")
        self.progress_bar.setValue(0)

        # Start download in a separate thread
        self.download_thread = QThread()
        self.download_worker = DownloadWorker(
            self.manga_data['title'],
            selected_chapters,
            conversion_type,
            delete_images
        )
        self.download_worker.moveToThread(self.download_thread)

        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.progress.connect(self.on_download_progress)
        
        self.download_worker.finished.connect(self.download_thread.quit)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_thread.finished.connect(self.download_thread.deleteLater)

        self.download_thread.start()

    def on_download_finished(self):
        self.download_button.setEnabled(True)
        self.download_button.setText("Download Selected Chapters")
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "Download and conversion completed!")

    def on_download_error(self, error_message):
        self.download_button.setEnabled(True)
        self.download_button.setText("Download Selected Chapters")
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "Error", f"An error occurred during download:\n{error_message}")

    def on_download_progress(self, message):
        # Update status label with the message
        self.status_label.setText(message)
        # For now, just update the progress bar
        # In a more advanced implementation, you could parse the message to get a percentage
        self.progress_bar.setValue(min(self.progress_bar.value() + 10, 100))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Sans-serif", 10))
    main_win = KunMangaDownloaderGUI()
    main_win.show()
    sys.exit(app.exec())