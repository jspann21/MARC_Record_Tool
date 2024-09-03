"""
This module defines the SearchTab class and the SearchWorker QThread for searching library catalogs.
It provides an interface for searching by ISBN or Title & Author and displays the results in a table.
"""
import json
import re
import urllib.parse
import webbrowser
import requests
import validators
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QInputDialog, QMessageBox, QMenu
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class SearchTab(QWidget):
    """
    A QWidget class that provides an interface for searching library catalogs by ISBN, title, and author.
    The results are displayed in a table, and users can add or edit library entries and initiate searches.
    """
    def __init__(self, parent=None):
        """
        Initialize the SearchTab instance with the parent widget.
        """
        super().__init__(parent)
        self.parent = parent
        self.libraries = []
        self.search_worker = None
        self.search_button = None

        # Initialize attributes that will be set up in init_ui
        self.isbn_input_search = None
        self.search_isbn_button = None
        self.title_input_search = None
        self.author_input_search = None
        self.search_title_author_button = None
        self.cancel_button = None
        self.clear_button = None
        self.add_library_button = None
        self.library_table = None

        self.init_ui()

    def init_ui(self):
        """
        Set up the user interface components of the SearchTab.
        """
        layout = QVBoxLayout(self)

        # Create and add the search groups
        search_isbn_group = self.create_search_isbn_group()
        search_title_author_group = self.create_search_title_author_group()
        controls_group = self.create_controls_group()

        search_layout = QHBoxLayout()
        search_layout.addWidget(search_isbn_group)
        search_layout.addWidget(search_title_author_group)
        search_layout.addWidget(controls_group)
        layout.addLayout(search_layout)

        # Create and add the library table
        self.library_table = self.create_library_table()
        layout.addWidget(self.library_table)

        self.setLayout(layout)
        self.load_urls()

    def create_search_isbn_group(self):
        """
        Create the search by ISBN group.
        """
        search_isbn_group = QGroupBox("Search by ISBN")
        main_isbn_layout = QVBoxLayout()

        isbn_input_layout = QHBoxLayout()
        isbn_input_layout.addWidget(QLabel("Enter ISBN:"))
        self.isbn_input_search = QLineEdit()
        self.isbn_input_search.setToolTip("Enter ISBN number.")
        isbn_input_layout.addWidget(self.isbn_input_search)

        isbn_button_layout = QHBoxLayout()
        self.search_isbn_button = QPushButton("ISBN search")
        self.search_isbn_button.clicked.connect(self.start_isbn_search)
        isbn_button_layout.addWidget(self.search_isbn_button)

        main_isbn_layout.addLayout(isbn_input_layout)
        main_isbn_layout.addLayout(isbn_button_layout)
        search_isbn_group.setLayout(main_isbn_layout)

        return search_isbn_group

    def create_search_title_author_group(self):
        """
        Create the search by Title & Author group.
        """
        search_title_author_group = QGroupBox("Search by Title && Author")
        main_layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Enter Title:"))
        self.title_input_search = QLineEdit()
        self.title_input_search.setToolTip("Enter the title of the book.")
        title_layout.addWidget(self.title_input_search)

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Enter Author:"))
        self.author_input_search = QLineEdit()
        self.author_input_search.setToolTip("Enter the author of the book.")
        author_layout.addWidget(self.author_input_search)

        button_layout = QHBoxLayout()
        self.search_title_author_button = QPushButton("Title && Author search")
        self.search_title_author_button.clicked.connect(self.start_title_author_search)
        button_layout.addWidget(self.search_title_author_button)

        main_layout.addLayout(title_layout)
        main_layout.addLayout(author_layout)
        main_layout.addLayout(button_layout)
        search_title_author_group.setLayout(main_layout)

        return search_title_author_group

    def create_controls_group(self):
        """
        Create the controls group.
        """
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_search)
        controls_layout.addWidget(self.cancel_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_statuses)
        controls_layout.addWidget(self.clear_button)
        self.add_library_button = QPushButton("Add Library")
        self.add_library_button.clicked.connect(self.add_library)
        controls_layout.addWidget(self.add_library_button)
        controls_group.setLayout(controls_layout)

        return controls_group

    def create_library_table(self):
        """
        Create the library table.
        """
        library_table = QTableWidget()
        library_table.setColumnCount(4)
        library_table.setHorizontalHeaderLabels(["Status", "Library Name", "ISBN URL", "Title & Author URL"])
        library_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        library_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        library_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        library_table.horizontalHeader().resizeSection(0, 80)
        library_table.setEditTriggers(QTableWidget.DoubleClicked)
        library_table.setContextMenuPolicy(Qt.CustomContextMenu)
        library_table.customContextMenuRequested.connect(self.library_context_menu)
        library_table.cellDoubleClicked.connect(self.handle_double_click)

        return library_table


    def load_urls(self):
        """
        Load the library URLs from a JSON file.
        If the file is not found or is invalid, an empty list is used.
        """
        try:
            with open("libraries.json", "r", encoding="utf-8") as file:
                self.libraries = json.load(file)
                self.populate_library_table()
        except (FileNotFoundError, json.JSONDecodeError):
            self.libraries = []
            self.parent.console_output.append("No library list file found. Please add a library.")

    def populate_library_table(self):
        """
        Populate the table widget with the loaded library data.
        """
        self.library_table.setRowCount(len(self.libraries))
        for i, library in enumerate(self.libraries):
            self.library_table.setItem(i, 0, QTableWidgetItem(""))
            self.library_table.setItem(i, 1, QTableWidgetItem(library["name"]))
            self.library_table.setItem(i, 2, QTableWidgetItem(library.get("isbn_url", "")))
            self.library_table.setItem(i, 3, QTableWidgetItem(library.get("title_author_url", "")))

            for col in range(4):
                item = self.library_table.item(i, col)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def save_urls(self):
        """
        Save the current list of libraries and their URLs to a JSON file.
        """
        with open("libraries.json", "w", encoding="utf-8") as file:
            json.dump(self.libraries, file, indent=4)

    def start_isbn_search(self):
        """
        Start the ISBN search process by triggering the SearchWorker thread.
        """
        if not self.libraries:
            QMessageBox.warning(self, "Error", "No libraries found. Please add a library first.")
            return

        isbn = self.isbn_input_search.text().strip()

        if not isbn:
            self.parent.console_output.append("ISBN field is empty. Cannot perform the search.")
            return

        self.clear_statuses()
        self.disable_all_buttons_except_cancel()

        self.search_worker = SearchWorker(self.libraries, None, "isbn", isbn, self.parent.console_output)
        self.search_worker.update_status.connect(self.update_status)
        self.search_worker.search_complete.connect(self.reset_buttons)
        self.search_worker.start()

    def start_title_author_search(self):
        """
        Start the title and author search process by triggering the SearchWorker thread.
        """
        if not self.libraries:
            QMessageBox.warning(self, "Error", "No libraries found. Please add a library first.")
            return

        title = self.title_input_search.text().strip()
        author = self.author_input_search.text().strip()

        if not title or not author:
            self.parent.console_output.append("Title or Author field is empty. Cannot perform the search.")
            return

        self.clear_statuses()
        self.disable_all_buttons_except_cancel()

        self.search_worker = SearchWorker(self.libraries, None, "title_author", (title, author), self.parent.console_output)
        self.search_worker.update_status.connect(self.update_status)
        self.search_worker.search_complete.connect(self.reset_buttons)
        self.search_worker.start()

    def search_again(self, row, search_type):
        """
        Retry the search for a specific library by ISBN or title and author.
        """
        self.disable_all_buttons_except_cancel()

        if search_type == "isbn":
            isbn = self.isbn_input_search.text().strip()
            if isbn:
                self.start_search("isbn", isbn, row)
            else:
                self.parent.console_output.append("ISBN field is empty. Cannot perform the search.")
                self.reset_buttons()
        elif search_type == "title_author":
            title = self.title_input_search.text().strip()
            author = self.author_input_search.text().strip()
            if title and author:
                self.start_search("title_author", (title, author), row)
            else:
                self.parent.console_output.append("Title or Author field is empty. Cannot perform the search.")
                self.reset_buttons()

    def start_search(self, search_type, search_value, row=None):
        """
        Start the search process with the given search type and value.
        """
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait()

        if search_type == "isbn" and not search_value.strip():
            self.parent.console_output.append("ISBN field is empty. Cannot perform the search.")
            return

        if search_type == "title_author" and not all(search_value):
            self.parent.console_output.append("Title or Author field is empty. Cannot perform the search.")
            return

        self.search_worker = SearchWorker(self.libraries, index=row, search_type=search_type,
                                          search_value=search_value, console_output=self.parent.console_output)
        self.search_worker.update_status.connect(self.update_status)
        self.search_worker.search_complete.connect(self.reset_buttons)
        self.search_worker.start()
        self.disable_all_buttons_except_cancel()

        if row is None:
            self.clear_statuses()
        else:
            self.library_table.item(row, 0).setText("")
            self.library_table.item(row, 0).setBackground(QColor(255, 255, 255))

        if search_type == "isbn" and search_value.strip():
            self.search_button = self.search_isbn_button
        elif search_type == "title_author" and all(search_value):
            self.search_button = self.search_title_author_button
        else:
            self.parent.console_output.append("Required fields are empty. Cannot perform the search.")
            return

        self.search_button.setEnabled(False)

    def cancel_search(self):
        """
        Cancel the currently running search and reset the UI elements accordingly.
        """
        if hasattr(self, "search_worker") and self.search_worker.isRunning():
            self.parent.console_output.append("Cancelling the current search...")
            self.search_worker.stop()
            self.search_worker.wait()

        for row in range(self.library_table.rowCount()):
            status_item = self.library_table.item(row, 0)
            if status_item.text() == "Searching...":
                status_item.setText("Canceled")
                status_item.setBackground(QColor(255, 165, 0))
                self.parent.console_output.append(f"{self.libraries[row]['name']}: Search canceled.")

        self.reset_buttons()

    def update_status(self, row, status, url):
        """
        Update the status of the search result in the table for the given row.
        """
        status_item = self.library_table.item(row, 0)
        status_item.setText(status)

        if status == "Found":
            status_item.setBackground(QColor(144, 238, 144))
            self.parent.console_output.append(f"{self.libraries[row]['name']}: Found - {url}")
        elif status == "Not Found":
            status_item.setBackground(QColor(255, 182, 193))
            self.parent.console_output.append(f"{self.libraries[row]['name']}: Not Found")
        elif status == "Error":
            status_item.setBackground(QColor(255, 165, 0))
            self.parent.console_output.append(f"{self.libraries[row]['name']}: Error accessing {url}")
        else:
            self.parent.console_output.append(f"{self.libraries[row]['name']}: {status}")

        status_item.setData(Qt.UserRole, url)
        status_item.setToolTip("Double-click to open link")
        self.library_table.scrollToItem(status_item)

    def disable_all_buttons_except_cancel(self):
        """
        Disable all buttons except for the cancel button to prevent concurrent operations.
        """
        self.search_isbn_button.setEnabled(False)
        self.search_title_author_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.add_library_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.repaint()

    def reset_buttons(self):
        """
        Re-enable all buttons after the search is complete or canceled.
        """
        self.search_isbn_button.setEnabled(True)
        self.search_title_author_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.clear_button.setEnabled(True)
        self.add_library_button.setEnabled(True)

    def clear_statuses(self):
        """
        Clear all statuses and reset the background color of the status column in the table.
        """
        for row in range(self.library_table.rowCount()):
            self.library_table.item(row, 0).setText("")
            self.library_table.item(row, 0).setBackground(QColor(255, 255, 255))
        self.parent.console_output.clear()
        self.parent.console_output.append("Cleared.")

    def add_library(self):
        """
        Add a new library entry to the list of libraries with user-specified URLs.
        """
        library_name, ok = QInputDialog.getText(self, "Enter the library name", "Library Name:")
        if not ok or not library_name.strip():
            return

        isbn_url = ""
        while True:
            isbn_url, ok = QInputDialog.getText(self, "Enter the ISBN search URL",
                                                "Enter the library ISBN search URL (use {isbn} as placeholder):",
                                                text=isbn_url)
            if not ok:
                return

            if "{title}" in isbn_url or "{author}" in isbn_url:
                QMessageBox.warning(self, "Invalid URL", "The ISBN URL cannot contain {title} or {author}.")
                continue

            if "{isbn}" not in isbn_url:
                QMessageBox.warning(self, "Invalid URL", "The ISBN URL must include {isbn} as a placeholder.")
                continue

            break

        title_author_url = ""
        while True:
            title_author_url, ok = QInputDialog.getText(self, "Enter the Title and Author search URL",
                                                        "Enter the Title and Author search URL (use {title} and {author} as placeholders):",
                                                        text=title_author_url)
            if not ok:
                return

            if "{isbn}" in title_author_url:
                QMessageBox.warning(self, "Invalid URL", "The Title & Author URL cannot contain {isbn}.")
                continue

            if "{title}" not in title_author_url or "{author}" not in title_author_url:
                QMessageBox.warning(self, "Invalid URL", "The Title & Author URL must include {title} and {author}.")
                continue

            break

        self.libraries.append({
            "name": library_name.strip(),
            "isbn_url": isbn_url.strip(),
            "title_author_url": title_author_url.strip()
        })
        self.populate_library_table()
        self.save_urls()
        self.parent.changes_made = True

    def library_context_menu(self, position):
        """
        Show a context menu for the library table with options to search, edit, or delete a library entry.
        """
        menu = QMenu()

        search_isbn_action = menu.addAction("Search ISBN")
        search_isbn_action.triggered.connect(lambda: self.search_again(self.library_table.currentRow(), "isbn"))

        search_title_author_action = menu.addAction("Search Title && Author")
        search_title_author_action.triggered.connect(lambda: self.search_again(self.library_table.currentRow(), "title_author"))

        edit_action = menu.addAction("Edit Library")
        edit_action.triggered.connect(self.edit_library)

        delete_action = menu.addAction("Delete library")
        delete_action.triggered.connect(self.delete_library)

        menu.exec_(self.library_table.viewport().mapToGlobal(position))

    def edit_library(self):
        """
        Edit an existing library entry's name and URLs.
        """
        row = self.library_table.currentRow()
        if row < 0:
            return

        original_library_name = self.library_table.item(row, 1).text()
        original_isbn_url = self.library_table.item(row, 2).text()
        original_title_author_url = self.library_table.item(row, 3).text()

        library_name, ok = QInputDialog.getText(self, "Edit Library", "Library Name:", text=original_library_name)
        if not ok or not library_name.strip():
            self.parent.console_output.append(f"No changes made to '{original_library_name}'.")
            return

        changes = []

        if library_name != original_library_name:
            changes.append(f"Library Name changed from '{original_library_name}' to '{library_name}'.")

        isbn_url, ok = QInputDialog.getText(self, "Edit ISBN URL", "Enter the library ISBN search URL (use {isbn} as placeholder):",
                                            text=original_isbn_url)
        if not ok:
            self.parent.console_output.append(f"No changes made to '{library_name}'.")
            return

        if "{title}" in isbn_url or "{author}" in isbn_url:
            QMessageBox.warning(self, "Invalid URL", "The ISBN URL cannot contain {title} or {author}.")
            return

        if "{isbn}" not in isbn_url:
            QMessageBox.warning(self, "Invalid URL", "The ISBN URL must include {isbn} as a placeholder.")
            return

        if not validators.url(isbn_url):
            QMessageBox.warning(self, "Invalid URL", "The ISBN URL is not a valid URL.")
            return

        if isbn_url != original_isbn_url:
            changes.append(f"ISBN URL changed from '{original_isbn_url}' to '{isbn_url}'.")

        title_author_url, ok = QInputDialog.getText(self, "Edit Title and Author URL", "Enter the Title and Author search URL (use {title} and {author} as placeholders):",
                                                    text=original_title_author_url)
        if not ok:
            self.parent.console_output.append(f"No changes made to '{library_name}'.")
            return

        if "{isbn}" in title_author_url:
            QMessageBox.warning(self, "Invalid URL", "The Title & Author URL cannot contain {isbn}.")
            return

        if "{title}" not in title_author_url or "{author}" not in title_author_url:
            QMessageBox.warning(self, "Invalid URL", "The Title & Author URL must include both {title} and {author}.")
            return

        if not validators.url(title_author_url):
            QMessageBox.warning(self, "Invalid URL", "The Title & Author URL is not a valid URL.")
            return

        if title_author_url != original_title_author_url:
            changes.append(f"Title & Author URL changed from '{original_title_author_url}' to '{title_author_url}'.")

        if changes:
            self.library_table.item(row, 1).setText(library_name)
            self.library_table.item(row, 2).setText(isbn_url)
            self.library_table.item(row, 3).setText(title_author_url)

            self.libraries[row]["name"] = library_name
            self.libraries[row]["isbn_url"] = isbn_url
            self.libraries[row]["title_author_url"] = title_author_url

            self.parent.console_output.append(f"Library '{library_name}' updated: " + "; ".join(changes))
            self.save_urls()
        else:
            self.parent.console_output.append(f"No changes made to '{library_name}'.")

        self.parent.changes_made = True

    def delete_library(self):
        """
        Delete the selected library from the list and table.
        """
        row = self.library_table.currentRow()
        if row >= 0:
            library_name = self.library_table.item(row, 1).text()
            url = self.library_table.item(row, 2).text() or self.library_table.item(row, 3).text()
            reply = QMessageBox.question(self, "Confirm Delete",
                                         f"Are you sure you want to delete '{library_name}' with URL '{url}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.library_table.removeRow(row)
                del self.libraries[row]
                self.parent.changes_made = True
                self.save_urls()

    def handle_double_click(self, row, column):
        """
        Handle double-click events on the library table to open the corresponding URL in a web browser.
        """
        if column == 0:
            item = self.library_table.item(row, column)
            url = item.data(Qt.UserRole)
            if url:
                webbrowser.open(url)


class SearchWorker(QThread):
    """
    A QThread class responsible for performing the search operations asynchronously.
    Emits signals to update the status and notify when the search is complete.
    """
    update_status = pyqtSignal(int, str, str)
    search_complete = pyqtSignal()

    def __init__(self, libraries, index=None, search_type=None, search_value=None, console_output=None):
        """
        Initialize the SearchWorker with the necessary parameters for performing the search.
        """
        super().__init__()
        self.libraries = libraries
        self.index = index
        self.search_type = search_type
        self.search_value = search_value
        self._is_running = True
        self.console_output = console_output

    def run(self):
        """
        Run the search process for the specified libraries. Update the status based on search results.
        """
        if not self._is_running:
            return

        libraries_to_process = [(self.index, self.libraries[self.index])] if self.index is not None else enumerate(self.libraries)

        for i, library in libraries_to_process:
            if not self._is_running:
                break

            url = self.construct_url(library)
            if not url:
                self.update_status.emit(i, "Error", "URL construction failed.")
                continue

            self.update_status.emit(i, "Searching...", url)

            try:
                if not self._is_running:
                    break

                response = requests.get(url, allow_redirects=True, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                if self.check_not_found_conditions(soup):
                    self.update_status.emit(i, "Not Found", url)
                    continue

                if self.check_found_conditions(soup, response) or self.check_general_results(response):
                    self.update_status.emit(i, "Found", response.url)
                else:
                    self.update_status.emit(i, "Not Found", url)

            except requests.exceptions.RequestException as e:
                self.log_error(i, f"Request error: {str(e)}")
                self.update_status.emit(i, "Error", url)

        self._is_running = False
        self.search_complete.emit()

    def construct_url(self, library):
        """
        Construct the URL based on the search type.
        """
        url = None
        if self.search_type == "isbn":
            url_template = library.get("isbn_url", "")
            isbn = self.search_value.strip()
            if not isbn:
                self.log_error(self.index, "ISBN field is empty. Cannot perform the search.")
                return None
            url = url_template.format(isbn=urllib.parse.quote(isbn))
        elif self.search_type == "title_author":
            url_template = library.get("title_author_url", "")
            title, author = self.search_value
            title, author = title.strip(), author.strip()
            if not title or not author:
                self.log_error(self.index, "Title or Author field is empty. Cannot perform the search.")
                return None
            url = url_template.format(title=urllib.parse.quote(title), author=urllib.parse.quote(author))
        return url

    def check_not_found_conditions(self, soup):
        """
        Check for various "not found" conditions in the HTML content.
        """
        text_without_scripts = ' '.join(soup.stripped_strings).lower()  # Join all text excluding script tags

        not_found_conditions = [
            any(phrase in text_without_scripts for phrase in [
                "no results found", "no matches found", "no entries found", "search resulted in no hits",
                "no results!", "your search found no results.", "no records found"
            ]),
            soup.find("h1", text=re.compile("no results", re.IGNORECASE)),
            soup.find("h1", text=re.compile("no results available", re.IGNORECASE)),
            soup.find("div", {"id": "documents", "class": "noresults"}),
            soup.find("tr", class_="yourEntryWouldBeHere")
        ]
        return any(not_found_conditions)

    def check_found_conditions(self, soup, response):
        """
        Check for various "found" conditions in the HTML content.
        Prioritize exact text searches over generic elements.
        """
        # Check if the response was redirected to a detailed item page (common in Koha)
        if response.history and len(response.history) > 0:
            return True

        found_conditions = [
            soup.find_all("tr", class_="browseEntry"),  # Generic result rows
            soup.find("span", class_="results-bar-item results-bar-item-record-count"),  # Result count bar
            self.check_meta_total_results(soup),  # Meta tag check for total results
            soup.find_all("div", class_=re.compile(r'document')),  # General document classes
            soup.find("div", class_="bibDisplayContentMain"),  # Bibliographic display section
            soup.find("div", class_="bibDisplayItemsMain"),  # Bibliographic item section
            soup.find("div", class_="bibliographicData"),  # Detailed bibliographic data (specific to full record)
            soup.find(text=re.compile(r'Results:\s*\d+', re.IGNORECASE)),  # "Results: X found"
            soup.find(id="numresults"),  # Number of results indicator
            soup.find("span", class_="results-bar-item results-bar-item-record-count"),  # Duplicate of earlier check, could be removed
            soup.find("div", class_="browseSearchtoolMessage"),  # Search tool messages, possibly a success message
            self.check_search_stats(soup),  # Custom check for search statistics
            soup.find("span", text=re.compile(r"\d+\s+(?:results?|result|of\s+results?)\s*found", re.IGNORECASE))  # Result count regex
        ]
        return any(found_conditions)

    def check_meta_total_results(self, soup):
        """
        Check the meta tag for total results.
        """
        total_results_meta = soup.find("meta", {"name": "totalResults"})
        if total_results_meta:
            try:
                return int(total_results_meta.get("content", "0")) > 0
            except ValueError:
                return False
        return False

    def check_general_results(self, response):
        """
        Check for general results using various regex patterns.
        """
        response_text_lower = response.text.lower()
        # Existing regex patterns to check for general results
        patterns = [
            r'\b(?:your\s+search\s+returned\s+|(\d+)\s+)(?:results?|result)\b',  # Example: "Your search returned 100 results"
            r'\bResults:\s*\d+',  # Example: "Results: 100"
            r'\b(\d+)\s+(?:results?|result)\s+found\b',  # Example: "100 results found"
            r'\b(\d+)-(\d+)\s+of\s+(\d+)\b'  # Example: "1-25 of 10000"
        ]

        for pattern in patterns:
            if re.search(pattern, response_text_lower):
                return True  # If any pattern matches, consider it as results found.
        return False  # Return False if no patterns match

    def check_search_stats(self, soup):
        """
        Check the search stats div for data-record-total attribute.
        """
        search_stats_div = soup.find("div", class_="search-stats")
        if search_stats_div and search_stats_div.get('data-record-total'):
            try:
                return int(search_stats_div['data-record-total']) > 0
            except ValueError:
                return False
        return False

    def stop(self):
        """
        Stop the search process by terminating the thread.
        """
        self._is_running = False
        self.wait()

    def log_error(self, index, message):
        """
        Log an error message to the console and update the status for the given library.
        """
        if self.console_output:
            self.console_output.append(f"Library {index}: {message}")
        self.update_status.emit(index, "Error", message)
