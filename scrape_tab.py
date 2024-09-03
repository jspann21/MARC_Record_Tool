"""
This module provides the ScrapeTab class for scraping MARC data from URLs and creating MARC records.
"""
from urllib.parse import urlparse, parse_qs  # Standard library import
from pymarc import Record, Field, Subfield
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QMessageBox, QFileDialog
)
import requests
from bs4 import BeautifulSoup
from utils import clean_filename  # Import the clean_filename function


class ScrapeTab(QWidget):
    """
    A class that represents the tab for scraping MARC data and creating MARC records.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.base_url = ""
        self.marc_record = None
        self.default_filename = ""

        # Group related attributes to reduce the number of instance attributes
        self.ui_elements = {
            "url_input": QLineEdit(),
            "output_window": QTextEdit(),
            "scrape_button": QPushButton("Scrape URL"),
            "create_marc_button": QPushButton("Create MARC Record"),
            "download_marc_button": QPushButton("Download MARC Record"),
            "clear_button": QPushButton("Clear")  # Add the Clear button here
        }

        # Layouts and widgets
        layout = QVBoxLayout()
        self.setup_url_input(layout)
        self.setup_buttons(layout)
        self.ui_elements["output_window"].setReadOnly(True)
        layout.addWidget(self.ui_elements["output_window"])
        self.setLayout(layout)

    def setup_url_input(self, layout):
        """Sets up the URL input field."""
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("MARC URL:"))
        url_layout.addWidget(self.ui_elements["url_input"])
        layout.addLayout(url_layout)

    def setup_buttons(self, layout):
        """Sets up the buttons for the scraping and MARC record creation."""
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.ui_elements["scrape_button"])
        buttons_layout.addWidget(self.ui_elements["create_marc_button"])
        buttons_layout.addWidget(self.ui_elements["download_marc_button"])
        buttons_layout.addWidget(self.ui_elements["clear_button"])
        self.ui_elements["scrape_button"].clicked.connect(self.scrape_url)
        self.ui_elements["create_marc_button"].clicked.connect(self.create_marc_record)
        self.ui_elements["download_marc_button"].clicked.connect(self.download_marc_record)
        self.ui_elements["clear_button"].clicked.connect(self.clear_fields)
        layout.addLayout(buttons_layout)

    def log(self, message):
        """Log a message to the main window's console output."""
        self.main_window.console_output.append(message)

    def clear_fields(self):
        """Clears the URL input, output window, and MARC data."""
        self.ui_elements["url_input"].clear()
        self.ui_elements["output_window"].clear()
        self.marc_record = None
        self.default_filename = ""
        self.log("Cleared.")

    def scrape_url(self):
        """Scrapes the MARC data from the provided URL."""
        url = self.ui_elements["url_input"].text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL.")
            return

        self.log(f"Scraping URL: {url}")
        parsed_url = urlparse(url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        try:
            if "primo.exlibrisgroup.com" in parsed_url.netloc:
                self.log("Detected Primo Ex Libris URL.")
                self.fetch_marc_data(parsed_url, source="primo")
            elif "discovery/sourceRecord" in parsed_url.path:
                self.log("Detected discovery/sourceRecord URL.")
                self.fetch_marc_data(parsed_url, source="discovery")
            else:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                self.parse_html(response.text)
        except requests.exceptions.RequestException as e:
            self.log(f"Error scraping URL: {e}")
            QMessageBox.critical(self, "Scraping Error", f"Failed to scrape the URL:\n{e}")


    def fetch_marc_data(self, parsed_url, source="primo"):
        """Fetches MARC data from a specified source."""
        query_params = parse_qs(parsed_url.query)
        doc_id, vid, record_owner = query_params.get('docId'), query_params.get('vid'), query_params.get('recordOwner')

        if not all([doc_id, vid, record_owner]):
            self.log(f"Failed to extract necessary parameters from {source} URL.")
            QMessageBox.critical(self, "URL Error", "Unable to extract necessary parameters from the URL.")
            return

        api_url = f"https://{parsed_url.netloc}/primaws/rest/pub/sourceRecord?docId={doc_id[0]}&vid={vid[0]}&recordOwner={record_owner[0]}&lang=en"

        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            self.parse_format_three(response.text)
        except requests.exceptions.RequestException as e:
            self.log(f"Error fetching MARC data from {source} API: {e}")
            QMessageBox.critical(self, "API Error", f"Failed to fetch MARC data from {source} API:\n{e}")

    def parse_html(self, html):
        """Parses the HTML content to detect the MARC format and extract data."""
        soup = BeautifulSoup(html, 'html.parser')
        parse_methods = {
            'format_one': self.parse_format_one,
            'format_two': self.parse_format_two,
            'format_three': self.parse_format_three,
            'format_four': self.parse_format_four
        }
        format_detected = None

        if soup.find('div', class_='field'):
            format_detected = 'format_one'
        elif soup.find('table', id='marc'):
            format_detected = 'format_two'
        elif soup.find('pre', style='direction: ltr'):
            format_detected = 'format_three'
        elif soup.find('table', class_='citation table table-striped'):
            format_detected = 'format_four'

        if format_detected:
            self.log(f"Detected {format_detected}.")
            parse_methods[format_detected](soup)
        else:
            self.log("Unknown format detected.")
            QMessageBox.critical(self, "Format Error", "Unable to identify the MARC format in the provided HTML.")



    def parse_format_one(self, soup):
        """Parses MARC data in format_one."""
        self.marc_record = Record()

        fields = soup.find_all('div', class_='field')
        for field in fields:
            tag_span = field.find('span', class_='tag')
            if not tag_span:
                continue

            tag = tag_span.get_text().strip()
            ind1 = field.find('div', class_='ind1').get_text().strip() \
                if field.find('div', class_='ind1') else ' '
            ind2 = field.find('div', class_='ind2').get_text().strip() \
                if field.find('div', class_='ind2') else ' '

            # Control fields do not have indicators
            indicators = None if tag in ['001', '003', '005', '008'] else [ind1, ind2]

            subfield_objs = []
            subfields = field.find_all('span', class_='sub_code')
            for subfield in subfields:
                code = subfield.get_text().strip().replace('|', '')
                value = subfield.next_sibling.strip() if subfield.next_sibling else ''
                subfield_objs.append(Subfield(code, value))

            if subfield_objs:
                try:
                    self.marc_record.add_field(Field(tag, indicators, subfields=subfield_objs))
                    self.ui_elements["output_window"].append(
                        f"{tag} {ind1}{ind2} "
                        f"{' '.join(f'${sf.code} {sf.value}' for sf in subfield_objs)}"
                    )
                except ValueError as e:
                    self.log(f"ValueError adding field {tag}: {str(e)}")
                except TypeError as e:
                    self.log(f"TypeError adding field {tag}: {str(e)}")
                except KeyError as e:
                    self.log(f"KeyError adding field {tag}: {str(e)}")
                except Exception as e:
                    self.log(f"Unexpected error adding field {tag}: {str(e)}")
                    raise

    def parse_format_two(self, soup):
        """Parses MARC data in format_two."""
        # First, identify and follow the "view plain" link
        view_plain_link = soup.find('a', id='switchview')
        if view_plain_link:
            plain_url = self.base_url + view_plain_link['href']
            self.log(f"Found 'view plain' link: {plain_url}")

            # Request the plain MARC data
            try:
                plain_response = requests.get(plain_url, timeout=10)
                plain_response.raise_for_status()
                self.parse_plain_marc(plain_response.text)
            except requests.exceptions.RequestException as e:
                self.log(f"Error fetching plain MARC data: {e}")
                QMessageBox.critical(self, "Fetch Error", f"Failed to fetch plain MARC data:\n{e}")
        else:
            self.log("ERROR: 'View plain' link not found. Cannot continue with format_two parsing.")
            QMessageBox.critical(self, "Parsing Error", "Unable to find the 'view plain' link.")

    def parse_format_three(self, marc_data):
        """Parses MARC data in format_three."""
        self.marc_record = Record()
        lines = marc_data.splitlines()

        for line in lines:
            if not line.strip() or line.startswith('leader'):
                continue  # Skip empty lines and the "leader" line

            # The first three characters represent the field tag
            tag = line[:3].strip()

            # Discard fields with tags from 000 to 009
            if tag.isdigit() and 0 <= int(tag) <= 9:
                self.log(f"Discarded field with tag {tag}: {line}")
                continue

            # Extract indicators
            ind1 = line[4] if len(line) > 4 and line[4] != ' ' else '\\'
            ind2 = line[5] if len(line) > 5 and line[5] != ' ' else '\\'

            # Replace '#' with '\' in indicators
            ind1 = '\\' if ind1 == '#' else ind1
            ind2 = '\\' if ind2 == '#' else ind2

            # Extract subfield data
            subfield_data = line[7:].strip()  # Subfield data starts after the indicators and space
            subfields = []

            # Split subfields based on the '$' delimiter
            if subfield_data:
                parts = subfield_data.split('$')
                for part in parts:
                    if part:
                        subfield_code = part[0]
                        subfield_value = part[1:].strip()
                        subfields.append(Subfield(subfield_code, subfield_value))

            # Add the field to the MARC record
            if subfields:
                self.marc_record.add_field(
                    Field(tag, indicators=[ind1, ind2], subfields=subfields)
                )
                # Display each field in the output window
                field_output = (
                    f"={tag}  {ind1}{ind2} {' '.join(f'${sf.code} {sf.value}' for sf in subfields)}"
                )
                self.ui_elements["output_window"].append(field_output)

        self.log(f"Finished parsing. Parsed {len(self.marc_record.get_fields())} fields.")
        self.update_filename()

    def parse_format_four(self, soup):
        """Parses MARC data in format_four."""
        self.marc_record = Record()

        # Locate the MARC table in the HTML
        marc_table = soup.find('table', class_='citation table table-striped')

        if not marc_table:
            self.log("ERROR: MARC table not found.")
            return

        rows = marc_table.find_all('tr')

        for row in rows:
            # Extract the tag (th), indicators (first two td), and subfield data (remaining td)
            tag_element = row.find('th')
            if not tag_element:
                continue

            tag = tag_element.get_text(strip=True)

            # Skip rows that are not MARC tags (like LEADER, etc.)
            if not tag.isdigit():
                continue

            cells = row.find_all('td')
            if len(cells) < 3:
                continue

            ind1 = cells[0].get_text(strip=True) or ' '
            ind2 = cells[1].get_text(strip=True) or ' '
            subfield_data = cells[2]

            subfields = []
            strong_tags = subfield_data.find_all('strong')

            for strong_tag in strong_tags:
                code = strong_tag.get_text(strip=True).replace('|', '')
                value = strong_tag.next_sibling.strip() if strong_tag.next_sibling else ''
                if code and value:
                    subfields.append(Subfield(code, value))

            if subfields:
                try:
                    self.marc_record.add_field(
                        Field(tag, indicators=[ind1, ind2], subfields=subfields)
                    )
                    # Display each field in the output window
                    field_output = (
                        f"={tag}  {ind1}{ind2} "
                        f"{' '.join(f'${sf.code} {sf.value}' for sf in subfields)}"
                    )

                    self.ui_elements["output_window"].append(field_output)
                except ValueError as e:
                    self.log(f"ValueError adding field {tag}: {str(e)}")
                except TypeError as e:
                    self.log(f"TypeError adding field {tag}: {str(e)}")
                except KeyError as e:
                    self.log(f"KeyError adding field {tag}: {str(e)}")
                except Exception as e:
                    self.log(f"Unexpected error adding field {tag}: {str(e)}")
                    raise

        self.log(f"Finished parsing. Parsed {len(self.marc_record.get_fields())} fields.")

    def parse_plain_marc(self, plain_text):
        """Parses plain MARC data."""
        self.marc_record = Record()

        # Define the tags and subfields to be discarded
        discard_subfields = {
            '100': ['9'],
            '600': ['9'],
            '650': ['9'],
            '700': ['9'],
            '830': ['9']
        }

        # Parse the plain text with BeautifulSoup
        plain_soup = BeautifulSoup(plain_text, 'html.parser')

        # Find the table containing the MARC data
        marc_table = plain_soup.find('table')

        if marc_table is None:
            self.log("ERROR: MARC table not found in the plain view.")
            return

        rows = marc_table.find_all('tr')
        current_tag = None
        indicators = ['', '']
        subfields = []

        for row in rows:
            cells = row.find_all('td')
            tag_element = row.find('th')

            if tag_element:
                # Handle a new MARC field
                current_tag = tag_element.get_text(strip=True)

                # Extract indicators (if available)
                if len(cells) >= 2:
                    ind1 = cells[0].get_text(strip=True) if cells[0].get_text(strip=True) else ' '
                    ind2 = cells[1].get_text(strip=True) if cells[1].get_text(strip=True) else ' '
                    indicators = [ind1, ind2]
                else:
                    indicators = ['', '']  # Default to blank indicators if not present

                subfields = []
                # Parse subfields from the current row
                if len(cells) > 2:
                    subfield_data = cells[2]  # The third <td> contains the subfield data
                    strong_tags = subfield_data.find_all('strong')

                    for strong_tag in strong_tags:
                        code = strong_tag.get_text(strip=True)
                        if code.startswith('_') and len(code) > 1:
                            subfield_code = code[1]  # Get the letter after '_'
                            value = strong_tag.next_sibling.strip() \
                                if strong_tag.next_sibling else ''

                            # Discard invalid subfields and log them
                            if (current_tag in discard_subfields and
                                subfield_code in discard_subfields[current_tag]):
                                self.log(
                                    f"Discarded subfield ${subfield_code} "
                                    f"in field {current_tag}: {value}"
                                )
                                continue

                            subfields.append(Subfield(subfield_code, value))

                    # Add the parsed field to the MARC record
                    if current_tag and subfields:
                        try:
                            self.marc_record.add_field(
                                Field(current_tag, indicators, subfields=subfields)
                            )
                            # Display each field in the output window
                            field_output = (
                                f"{current_tag} {ind1}{ind2} "
                                f"{' '.join(f'${sf.code} {sf.value}' for sf in subfields)}"
                            )
                            self.ui_elements["output_window"].append(field_output)
                        except ValueError as e:
                            self.log(f"ValueError adding field {current_tag}: {str(e)}")
                        except TypeError as e:
                            self.log(f"TypeError adding field {current_tag}: {str(e)}")
                        except KeyError as e:
                            self.log(f"KeyError adding field {current_tag}: {str(e)}")
                        except Exception as e:
                            self.log(f"Unexpected error adding field {current_tag}: {str(e)}")
                            raise

        # Log the number of parsed fields
        self.log(f"Finished parsing. Parsed {len(self.marc_record.get_fields())} fields.")

        # Update the filename using the parsed fields and sanitize it
        self.update_filename()

    def create_marc_record(self):
        """Creates a MARC record."""
        if not self.marc_record:
            QMessageBox.warning(
                self, "No MARC Data", "No MARC data has been parsed to create a record."
            )
            return

        # Perform validation
        if not self.validate_marc_record():
            QMessageBox.critical(
                self, "Validation Error", "MARC record failed validation. Please correct the issues."
            )
            return

        self.log("MARC record created and validated successfully.")
        # Additional functionality for creating and processing MARC record can be added here

    def validate_marc_record(self):
        """Validates the MARC record for required fields and proper format."""
        required_fields = ['001', '245']  # Example: 001 is control number, 245 is title
        for tag in required_fields:
            if not self.marc_record.get_fields(tag):
                self.log(f"Validation Error: Required field {tag} is missing.")
                return False

        # Additional validation logic here
        # For example, ensure no duplicate 001 field
        control_number_fields = self.marc_record.get_fields('001')
        if len(control_number_fields) > 1:
            self.log("Validation Error: Multiple 001 fields found.")
            return False

        # Ensure title field (245) has a subfield 'a' (main title)
        title_fields = self.marc_record.get_fields('245')
        if title_fields:
            main_title_subfield = any(sf.code == 'a' for sf in title_fields[0].subfields)
            if not main_title_subfield:
                self.log("Validation Error: Field 245 is missing subfield 'a' for the main title.")
                return False

        return True

    def update_filename(self):
        """Update the filename based on the 100 and 245 fields and sanitize it."""
        if not self.marc_record:
            return

        title = ''
        author = ''
        for field in self.marc_record.get_fields('245', '100'):
            subfields = field.subfields
            for subfield in subfields:
                if field.tag == '245' and subfield.code == 'a':
                    title = subfield.value.strip()
                elif field.tag == '100' and subfield.code == 'a':
                    author = subfield.value.strip()

        if not author:
            author = "UnknownAuthor"
        if not title:
            title = "Untitled"

        self.default_filename = clean_filename(f"{author}_{title}")
        self.log(f"Filename set to {self.default_filename}")

    def download_marc_record(self):
        """Downloads the MARC record to a file."""
        if not self.marc_record:
            QMessageBox.warning(self, "No MARC Data", "No MARC record is available to download.")
            return

        default_filename = getattr(self, 'default_filename', 'marc_record.mrc')
        save_path = QFileDialog.getSaveFileName(
            None, "Save MARC Record", default_filename, "MARC Files (*.mrc)")[0]

        if save_path:
            try:
                with open(save_path, 'wb') as file:
                    file.write(self.marc_record.as_marc())
                self.log(f"MARC record saved successfully at {save_path}.")
            except IOError as e:
                self.log(f"File I/O error: {str(e)}")
                QMessageBox.critical(
                    None, "Error", f"An error occurred during MARC record saving: {str(e)}"
                )
        else:
            self.log("Save operation was cancelled.")
