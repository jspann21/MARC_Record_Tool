"""
This module defines the main application window for the MARC Record Tool. It integrates
different tabs for cataloging, searching libraries, and scraping MARC records.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit, QLabel,
                             QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QMessageBox)
from cataloging_tab import CatalogingTab
from search_tab import SearchTab
from scrape_tab import ScrapeTab

class ISBNQueryApp(QMainWindow):
    """Main application window for the MARC Record Tool."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MARC Record Tool")
        self.setGeometry(100, 100, 1200, 800)

        self.tab_widget = QTabWidget()

        self.cataloging_tab = CatalogingTab(self)
        self.search_tab = SearchTab(self)
        self.scrape_tab = ScrapeTab(self)

        # Add tabs
        self.tab_widget.addTab(self.cataloging_tab, "Original Cataloging")
        self.tab_widget.addTab(self.search_tab, "Search Libraries")
        self.tab_widget.addTab(self.scrape_tab, "Scrape MARC")

        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)
        self.console_output.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.console_output.setMinimumHeight(150)

        # Main layout combining tab widget and log output
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(QLabel("Log"))
        main_layout.addWidget(self.console_output)

        # Help button in the top right corner
        help_button_layout = QHBoxLayout()
        help_button_layout.addStretch(1)  # Add stretch to push the button to the right
        help_button = QPushButton("Help")
        help_button.setToolTip("Click for help.")
        help_button.clicked.connect(self.show_help)
        help_button.setFixedWidth(50)
        help_button_layout.addWidget(help_button)

        # Add the help button layout to the main layout
        main_layout.addLayout(help_button_layout)

        # Set the main layout as the layout for the container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.changes_made = False

    def closeEvent(self, event):
        """
        Handles the close event. Ensures that any running threads are stopped,
        prompts the user to save changes, and performs resource cleanup.
        """
        # Stop and wait for SearchWorker thread to finish
        if hasattr(self, 'search_worker') and self.search_worker.isRunning():
            self.console_output.append("Stopping search worker...")
            self.search_worker.stop()
            self.search_worker.wait()

        # Save URLs or any other data if changes were made
        if self.changes_made:
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                "Do you want to save the changes to the library list before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.save_urls()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

        # Clean up any other resources
        self.cleanup_resources()

        # Log that the application is closing
        self.console_output.append("Application is closing...")

        # Call the superclass closeEvent to ensure the event loop terminates correctly
        event.accept()

    def cleanup_resources(self):
        """Placeholder for resource cleanup, e.g., closing files, network connections."""

    def show_help(self):
        """Displays help information in a message box."""
        help_text = (
            "<b>Version 0.1</b><br>"
            "<b>Original Cataloging Tab:</b><br>"
            "Enter as much information as available.<br>"
            "<b>Create MARC</b> will use the information created to create a MARC record, "
            "but will not save it.<br>"
            "<b>Download MARC</b> will download the created MARC record and prompt where "
            "to save it.<br>"
            "<b>Search Libraries</b> will send the ISBN, Title, and Author to the 'Search "
            "Libraries' tab where those searches can be run, if so desired.<br><br>"
            "<b>Search Libraries Tab:</b><br>"
            "Enter the ISBN or the Title and Author to search other libraries that have "
            "downloadable MARC records.<br>"
            "<b>Cancel</b> will cancel the search.<br>"
            "<b>Add Library</b> will allow you to add a new library. You must enter the "
            "search URLs for an ISBN-only search and one for a Title and Author search, "
            "using {isbn}, {title}, and {author} as placeholders.<br>"
            "It is too complicated and unnecessary to parse an ISBN, title, and author "
            "search URL if only the ISBN or only the title and author are provided.<br>"
            "<b>Status</b> is clickable to take you to the URL that was searched.<br>"
            "- <b>Found:</b> Indicates the book was found.<br>"
            "- <b>Not found:</b> Means the book was not found.<br>"
            "- <b>Timeout:</b> Means the search took too long and was cancelled.<br>"
            "- <b>Error:</b> Means there was an error for that search.<br>"
            "<b>Library Name:</b> The name of the library. This is arbitrary and doesn't "
            "matter. The field can be clicked and edited.<br>"
            "<b>ISBN URL:</b> The search URL for the ISBN with {isbn} where the ISBN number "
            "would appear in the search URL. You can click and edit this field.<br>"
            "<b>Title & Author URL:</b> The search URL for the Title and Author with {title} "
            "and {author} where they would appear in the search URL. You can click and "
            "edit this field.<br>"
            "Right-click options:<br>"
            "- <b>Search ISBN again:</b> Allows you to search that one URL again with the "
            "information that has been entered.<br>"
            "- <b>Search Title & Author again:</b> Allows you to search that one URL again "
            "with the information that has been entered.<br>"
            "- <b>Delete library:</b> Deletes the library from the search list.<br>"
            "When the window is closed, it will prompt you if you want to save the edited "
            "library list if the libraries have changed. This will create a .json file "
            "that contains the list of libraries."
        )

        QMessageBox.information(self, "Help", help_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ISBNQueryApp()
    window.show()
    sys.exit(app.exec_())
