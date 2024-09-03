"""
This module defines the CatalogingTab class for creating and downloading MARC records.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout,
    QGroupBox, QHBoxLayout, QRadioButton, QButtonGroup
)
from utils import create_marc_record, download_marc_record

class CatalogingTab(QWidget):
    """A tab for cataloging books and creating MARC records."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.marc_record = None  # Store the MARC record here
        self.marc_filename = ""  # Initialize the MARC filename

        # Grouping related attributes into dictionaries to reduce instance attributes
        self.inputs = {}
        self.radio_buttons = {}
        self.buttons = {}

        self.init_ui()

    def init_ui(self):
        """Initializes the user interface for the cataloging tab."""
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        self.setup_instructions(layout)
        self.setup_title_fields(grid_layout)
        self.setup_author_fields(grid_layout)
        self.setup_publisher_fields(grid_layout)
        self.setup_misc_fields(grid_layout)
        self.setup_buttons(layout, grid_layout)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def setup_instructions(self, layout):
        """Sets up the instructions section."""
        instructions_group_box = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()
        instructions_label = QLabel(
            "1. Enter as much information as available. Hover over entry fields for tips.\n"
            "2. Click 'Create MARC' after all available information has been entered.\n"
            "3. Click 'Download MARC' after the record has been created."
        )
        instructions_layout.addWidget(instructions_label)
        instructions_group_box.setLayout(instructions_layout)
        layout.addWidget(instructions_group_box)

    def setup_title_fields(self, grid_layout):
        """Sets up title-related fields."""
        self.inputs['title_input'] = QLineEdit()
        self.inputs['title_input'].setToolTip("Enter the title of the book.")
        grid_layout.addWidget(QLabel("Title:"), 0, 0)
        grid_layout.addWidget(self.inputs['title_input'], 0, 1)

        self.inputs['subtitle_input'] = QLineEdit()
        self.inputs['subtitle_input'].setToolTip("Leave empty if no subtitle.")
        grid_layout.addWidget(QLabel("Subtitle:"), 1, 0)
        grid_layout.addWidget(self.inputs['subtitle_input'], 1, 1)

    def setup_author_fields(self, grid_layout):
        """Sets up author-related fields."""
        self.inputs['author_input'] = QLineEdit()
        self.inputs['author_input'].setToolTip(
            "Enter all names as Last, First Middle, Suffix. Enter names exactly as they appear."
        )
        grid_layout.addWidget(QLabel("Author:"), 2, 0)
        grid_layout.addWidget(self.inputs['author_input'], 2, 1)

        self.inputs['second_author_input'] = QLineEdit()
        self.inputs['second_author_input'].setToolTip(
            "Enter all names as Last, First Middle, Suffix. Enter names exactly as they appear."
        )
        grid_layout.addWidget(QLabel("Second Author:"), 3, 0)
        grid_layout.addWidget(self.inputs['second_author_input'], 3, 1)

        self.inputs['third_author_input'] = QLineEdit()
        self.inputs['third_author_input'].setToolTip(
            "Enter all names as Last, First Middle, Suffix. Enter names exactly as they appear."
        )
        grid_layout.addWidget(QLabel("Third Author:"), 4, 0)
        grid_layout.addWidget(self.inputs['third_author_input'], 4, 1)

    def setup_publisher_fields(self, grid_layout):
        """Sets up publisher-related fields."""
        self.inputs['editor_input'] = QLineEdit()
        self.inputs['editor_input'].setToolTip(
            "Enter all names as Last, First Middle, Suffix. Enter names exactly as they appear."
        )
        grid_layout.addWidget(QLabel("Editor:"), 5, 0)
        grid_layout.addWidget(self.inputs['editor_input'], 5, 1)

        self.inputs['second_editor_input'] = QLineEdit()
        self.inputs['second_editor_input'].setToolTip(
            "Enter all names as Last, First Middle, Suffix. Enter names exactly as they appear."
        )
        grid_layout.addWidget(QLabel("Second Editor:"), 6, 0)
        grid_layout.addWidget(self.inputs['second_editor_input'], 6, 1)

        self.inputs['copyright_year_input'] = QLineEdit()
        self.inputs['copyright_year_input'].setToolTip("Enter the copyright year of the book.")
        grid_layout.addWidget(QLabel("Copyright Year:"), 7, 0)
        grid_layout.addWidget(self.inputs['copyright_year_input'], 7, 1)

        self.inputs['edition_input'] = QLineEdit()
        self.inputs['edition_input'].setToolTip(
            "Enter the edition. Leave empty if no edition given."
        )
        grid_layout.addWidget(QLabel("Edition:"), 8, 0)
        grid_layout.addWidget(self.inputs['edition_input'], 8, 1)

        self.inputs['publisher_input'] = QLineEdit()
        self.inputs['publisher_input'].setToolTip("Enter the publisher of the book.")
        grid_layout.addWidget(QLabel("Publisher:"), 9, 0)
        grid_layout.addWidget(self.inputs['publisher_input'], 9, 1)

        self.inputs['publisher_location_input'] = QLineEdit()
        self.inputs['publisher_location_input'].setToolTip(
            "Write the publisher's location exactly as it appears on the title page or verso."
        )
        grid_layout.addWidget(QLabel("Publisher Location:"), 10, 0)
        grid_layout.addWidget(self.inputs['publisher_location_input'], 10, 1)

    def setup_misc_fields(self, grid_layout):
        """Sets up miscellaneous fields."""
        self.setup_lccn_field(grid_layout)
        self.setup_isbn_fields(grid_layout)
        self.setup_call_number_field(grid_layout)
        self.setup_physical_description_fields(grid_layout)
        self.setup_references_fields(grid_layout)
        self.setup_summary_and_subject_fields(grid_layout)

    def setup_lccn_field(self, grid_layout):
        """Sets up the LCCN field."""
        self.inputs['lccn_input'] = QLineEdit()
        self.inputs['lccn_input'].setToolTip(
            "Leave empty if no Library of Congress Control Number (LCCN)."
        )
        grid_layout.addWidget(QLabel("LCCN:"), 11, 0)
        grid_layout.addWidget(self.inputs['lccn_input'], 11, 1)

    def setup_isbn_fields(self, grid_layout):
        """Sets up the ISBN fields."""
        self.inputs['isbn_input'] = QLineEdit()
        self.inputs['isbn_input'].setToolTip("Enter ISBN number.")
        grid_layout.addWidget(QLabel("ISBN:"), 12, 0)
        grid_layout.addWidget(self.inputs['isbn_input'], 12, 1)

        self.inputs['second_isbn_input'] = QLineEdit()
        self.inputs['second_isbn_input'].setToolTip("Leave empty if only one ISBN number.")
        grid_layout.addWidget(QLabel("Second ISBN:"), 13, 0)
        grid_layout.addWidget(self.inputs['second_isbn_input'], 13, 1)

    def setup_call_number_field(self, grid_layout):
        """Sets up the Library of Congress Call Number field."""
        self.inputs['loc_call_number_input'] = QLineEdit()
        self.inputs['loc_call_number_input'].setToolTip("Leave blank if no call number.")
        grid_layout.addWidget(QLabel("Library of Congress Call Number:"), 14, 0)
        grid_layout.addWidget(self.inputs['loc_call_number_input'], 14, 1)

    def setup_physical_description_fields(self, grid_layout):
        """Sets up the physical description fields."""
        self.inputs['pages_input'] = QLineEdit()
        self.inputs['pages_input'].setToolTip("Enter the number of pages.")
        grid_layout.addWidget(QLabel("Number of Pages:"), 15, 0)
        grid_layout.addWidget(self.inputs['pages_input'], 15, 1)

        self.inputs['book_height_input'] = QLineEdit()
        self.inputs['book_height_input'].setToolTip("Measure in cm and round up.")
        grid_layout.addWidget(QLabel("Book height (cm):"), 16, 0)
        grid_layout.addWidget(self.inputs['book_height_input'], 16, 1)

    def setup_references_fields(self, grid_layout):
        """Sets up the bibliographic references fields."""
        # Bibliographic references
        grid_layout.addWidget(QLabel("Bibliographic references?"), 17, 0)
        self.radio_buttons['references_yes_radio'] = QRadioButton("Yes")
        self.radio_buttons['references_no_radio'] = QRadioButton("No")
        references_button_group = QButtonGroup(self)  # Group the references radio buttons
        references_button_group.addButton(self.radio_buttons['references_yes_radio'])
        references_button_group.addButton(self.radio_buttons['references_no_radio'])
        references_layout = QHBoxLayout()
        references_layout.addWidget(self.radio_buttons['references_yes_radio'])
        references_layout.addWidget(self.radio_buttons['references_no_radio'])
        grid_layout.addLayout(references_layout, 17, 1)

        # Bibliographical references page range
        grid_layout.addWidget(QLabel("Bibliographical references page range:"), 18, 0)
        self.inputs['references_page_range_input'] = QLineEdit()
        self.inputs['references_page_range_input'].setToolTip(
            "If the book has an 'endnotes', 'references', or 'works cited' "
            "section at the end of the book, list the page range here."
        )
        grid_layout.addWidget(self.inputs['references_page_range_input'], 18, 1)

    def setup_summary_and_subject_fields(self, grid_layout):
        """Sets up the summary and LOC Subject Heading fields."""
        # Index
        grid_layout.addWidget(QLabel("Index?"), 19, 0)
        self.radio_buttons['index_yes_radio'] = QRadioButton("Yes")
        self.radio_buttons['index_no_radio'] = QRadioButton("No")
        index_button_group = QButtonGroup(self)  # Group the index radio buttons
        index_button_group.addButton(self.radio_buttons['index_yes_radio'])
        index_button_group.addButton(self.radio_buttons['index_no_radio'])
        index_layout = QHBoxLayout()
        index_layout.addWidget(self.radio_buttons['index_yes_radio'])
        index_layout.addWidget(self.radio_buttons['index_no_radio'])
        grid_layout.addLayout(index_layout, 19, 1)

        # Summary
        self.inputs['summary_input'] = QLineEdit()
        self.inputs['summary_input'].setToolTip(
            "Summary from the back of the book (or inside flap of hardback). "
            "Do not include 'praise for this book' type of blurbs."
        )
        grid_layout.addWidget(QLabel("Summary:"), 20, 0)
        grid_layout.addWidget(self.inputs['summary_input'], 20, 1)

        # LOC Subject Headings
        self.inputs['loc_subject_1_input'] = QLineEdit()
        self.inputs['loc_subject_1_input'].setToolTip(
            "Enter Library of Congress Subject Headings. Use link to search for standard headings."
        )
        grid_layout.addWidget(QLabel("LOC Subject Heading 1:"), 21, 0)
        grid_layout.addWidget(self.inputs['loc_subject_1_input'], 21, 1)

        self.inputs['loc_subject_2_input'] = QLineEdit()
        self.inputs['loc_subject_2_input'].setToolTip(
            "Enter Library of Congress Subject Headings. Use link to search for standard headings."
        )
        grid_layout.addWidget(QLabel("LOC Subject Heading 2:"), 22, 0)
        grid_layout.addWidget(self.inputs['loc_subject_2_input'], 22, 1)

        self.inputs['loc_subject_3_input'] = QLineEdit()
        self.inputs['loc_subject_3_input'].setToolTip(
            "Enter Library of Congress Subject Headings. Use link to search for standard headings."
        )
        grid_layout.addWidget(QLabel("LOC Subject Heading 3:"), 23, 0)
        grid_layout.addWidget(self.inputs['loc_subject_3_input'], 23, 1)

        loc_subjects_help_link = QLabel(
            '<a href="https://id.loc.gov/authorities/subjects.html">'
            'Click here to search for LOC Subject Headings</a>'
        )
        loc_subjects_help_link.setOpenExternalLinks(True)
        grid_layout.addWidget(loc_subjects_help_link, 24, 1)


    def setup_buttons(self, layout, grid_layout):
        """Sets up the buttons."""
        buttons_layout = QHBoxLayout()
        self.buttons['create_marc_button'] = QPushButton("Create MARC")
        self.buttons['create_marc_button'].setToolTip("Click to create MARC Record.")
        self.buttons['create_marc_button'].clicked.connect(self.create_marc_record)
        buttons_layout.addWidget(self.buttons['create_marc_button'])

        self.buttons['download_marc_button'] = QPushButton("Download MARC")
        self.buttons['download_marc_button'].setToolTip("Click to download MARC Record.")
        self.buttons['download_marc_button'].setEnabled(False)
        self.buttons['download_marc_button'].clicked.connect(self.download_marc_record)
        buttons_layout.addWidget(self.buttons['download_marc_button'])

        self.buttons['search_libraries_button'] = QPushButton("Search Libraries")
        self.buttons['search_libraries_button'].setToolTip(
            "Click to search other libraries for available MARC records to download."
        )
        self.buttons['search_libraries_button'].clicked.connect(self.switch_to_search_libraries)
        buttons_layout.addWidget(self.buttons['search_libraries_button'])

        layout.addLayout(grid_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def create_marc_record(self):
        """Creates a MARC record using the input data."""
        data = {
            'title': self.inputs['title_input'].text().strip(),
            'subtitle': self.inputs['subtitle_input'].text().strip(),
            'author': self.inputs['author_input'].text().strip(),
            'second_author': self.inputs['second_author_input'].text().strip(),
            'third_author': self.inputs['third_author_input'].text().strip(),
            'editor': self.inputs['editor_input'].text().strip(),
            'second_editor': self.inputs['second_editor_input'].text().strip(),
            'copyright_year': self.inputs['copyright_year_input'].text().strip(),
            'edition': self.inputs['edition_input'].text().strip(),
            'publisher': self.inputs['publisher_input'].text().strip(),
            'publisher_location': self.inputs['publisher_location_input'].text().strip(),
            'lccn': self.inputs['lccn_input'].text().strip(),
            'isbn': self.inputs['isbn_input'].text().strip(),
            'second_isbn': self.inputs['second_isbn_input'].text().strip(),
            'loc_call_number': self.inputs['loc_call_number_input'].text().strip(),
            'pages': self.inputs['pages_input'].text().strip(),
            'book_height': self.inputs['book_height_input'].text().strip(),
            'references': self.radio_buttons['references_yes_radio'].isChecked(),
            'references_page_range': self.inputs['references_page_range_input'].text().strip(),
            'index': self.radio_buttons['index_yes_radio'].isChecked(),
            'summary': self.inputs['summary_input'].text().strip(),
            'loc_subject_1': self.inputs['loc_subject_1_input'].text().strip(),
            'loc_subject_2': self.inputs['loc_subject_2_input'].text().strip(),
            'loc_subject_3': self.inputs['loc_subject_3_input'].text().strip(),
        }

        self.marc_record = create_marc_record(
            console_output=self.parent.console_output,
            data=data
        )

        if self.parent:
            self.parent.console_output.append("MARC Record created and ready to download.")
        self.buttons['download_marc_button'].setEnabled(True)


    def download_marc_record(self):
        """Downloads the created MARC record to a file."""
        if not self.marc_record:
            if self.parent:
                self.parent.console_output.append("No MARC record is available to download.")
            return

        # Use title and author from the form to create a default filename
        title = self.inputs['title_input'].text().strip()
        author = self.inputs['author_input'].text().strip()
        self.marc_filename = f"{title.replace(' ', '_')}_{author.replace(' ', '_')}.mrc"

        download_marc_record(self.marc_record, title, author, self.parent.console_output)
        self.buttons['download_marc_button'].setEnabled(False)

    def switch_to_search_libraries(self):
        """Switches to the Search Libraries tab with pre-filled data."""
        # Access the search tab via self.parent.search_tab
        self.parent.search_tab.isbn_input_search.setText(self.inputs['isbn_input'].text().strip())
        self.parent.search_tab.title_input_search.setText(self.inputs['title_input'].text().strip())
        self.parent.search_tab.author_input_search.setText(
            self.inputs['author_input'].text().strip()
        )

        # Switch to the Search Libraries tab
        self.parent.tab_widget.setCurrentIndex(1)
