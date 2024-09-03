"""
This module contains utilities for creating and downloading MARC records.
"""

import re
from pymarc import Record, Field, Subfield
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextEdit


class LineHighlightingTextEdit(QTextEdit):
    """
    A QTextEdit subclass that highlights the entire line where the mouse is clicked.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def mousePressEvent(self, event):  # pylint: disable=invalid-name
        """
        Highlights the line under the cursor when the mouse is pressed.
        """
        cursor = self.cursorForPosition(event.pos())
        cursor.select(cursor.LineUnderCursor)
        self.setTextCursor(cursor)
        super().mousePressEvent(event)


def create_marc_record(console_output, data):
    """
    Creates a MARC record based on the provided bibliographic information.

    :param console_output: QTextEdit for logging output.
    :param data: A dictionary containing bibliographic details.
    :return: MARC record in binary format.
    """

    if console_output:
        console_output.append("Creating MARC record...")

    record = Record()

    # Title (245) and subtitle, ensure 'c' subfield is not included here for author
    if data.get('title'):
        record.add_field(Field(tag='245', indicators=['1', '0'], subfields=[
            Subfield('a', data['title']),
            Subfield('b', data['subtitle'])
        ]))

    # Primary Author (100)
    if data.get('author'):
        record.add_field(Field(tag='100', indicators=['1', ' '], subfields=[
            Subfield('a', data['author'])
        ]))

    # Second and third authors (700)
    add_author_fields(record, data.get('second_author'), data.get('third_author'))

    # Editors (700)
    add_editor_fields(record, data.get('editor'), data.get('second_editor'))

    # LCCN (010)
    add_lccn_field(record, data.get('lccn'))

    # ISBNs (020)
    add_isbn_fields(record, data.get('isbn'), data.get('second_isbn'))

    # LOC Call Number (050)
    add_loc_call_number_field(record, data.get('loc_call_number'))

    # Publisher and location (264 for publication with indicator 1)
    add_publisher_and_copyright_fields(
        record,
        data.get('publisher_location'),
        data.get('publisher'),
        data.get('copyright_year')
    )

    # Edition (250)
    if data.get('edition'):
        record.add_field(Field(tag='250', indicators=[' ', ' '], subfields=[
            Subfield('a', data['edition'])
        ]))

    # Physical description (300)
    add_physical_description_field(record, data.get('pages'), data.get('book_height'))

    # Bibliographic references (504)
    add_references_field(record, data.get('references'), data.get('references_page_range'))

    # Index (500)
    if data.get('index'):
        record.add_field(Field(tag='500', indicators=[' ', ' '], subfields=[
            Subfield('a', "Includes index.")
        ]))

    # Summary (520)
    if data.get('summary'):
        record.add_field(Field(tag='520', indicators=[' ', ' '], subfields=[
            Subfield('a', data['summary'])
        ]))

    # LOC Subject Headings (650)
    add_loc_subject_headings(
        record,
        data.get('loc_subject_1'),
        data.get('loc_subject_2'),
        data.get('loc_subject_3')
    )

    return record.as_marc()

def add_author_fields(record, second_author, third_author):
    """
    Adds secondary and tertiary authors to the MARC record.
    """
    if second_author:
        record.add_field(Field(tag='700', indicators=['1', ' '], subfields=[
            Subfield('a', second_author)
        ]))
    if third_author:
        record.add_field(Field(tag='700', indicators=['1', ' '], subfields=[
            Subfield('a', third_author)
        ]))


def add_editor_fields(record, editor, second_editor):
    """
    Adds editors to the MARC record.
    """
    if editor:
        record.add_field(Field(tag='700', indicators=['1', ' '], subfields=[
            Subfield('a', editor)
        ]))
    if second_editor:
        record.add_field(Field(tag='700', indicators=['1', ' '], subfields=[
            Subfield('a', second_editor)
        ]))


def add_lccn_field(record, lccn):
    """
    Adds LCCN to the MARC record.
    """
    if lccn:
        record.add_field(Field(tag='010', indicators=[' ', ' '], subfields=[
            Subfield('a', lccn)
        ]))


def add_isbn_fields(record, isbn, second_isbn):
    """
    Adds ISBNs to the MARC record.
    """
    if isbn:
        record.add_field(Field(tag='020', indicators=[' ', ' '], subfields=[
            Subfield('a', isbn)
        ]))
    if second_isbn:
        record.add_field(Field(tag='020', indicators=[' ', ' '], subfields=[
            Subfield('a', second_isbn)
        ]))


def add_loc_call_number_field(record, loc_call_number):
    """
    Adds LOC Call Number to the MARC record.
    """
    if loc_call_number:
        record.add_field(Field(tag='050', indicators=['0', '4'], subfields=[
            Subfield('a', loc_call_number)
        ]))


def add_publisher_and_copyright_fields(record, publisher_location, publisher, copyright_year):
    """
    Adds publisher and copyright information to the MARC record.
    """
    if publisher or publisher_location or copyright_year:
        record.add_field(Field(tag='264', indicators=[' ', '1'], subfields=[
            Subfield('a', publisher_location),
            Subfield('b', publisher),
            Subfield('c', f"{copyright_year}")
        ]))
    if copyright_year:
        record.add_field(Field(tag='264', indicators=[' ', '4'], subfields=[
            Subfield('c', f"c{copyright_year}.")
        ]))


def add_physical_description_field(record, pages, book_height):
    """
    Adds physical description (pages and book height) to the MARC record.
    """
    if pages or book_height:
        record.add_field(Field(tag='300', indicators=[' ', ' '], subfields=[
            Subfield('a', f"{pages} p."),
            Subfield('c', f"{book_height} cm.")
        ]))


def add_references_field(record, references, references_page_range):
    """
    Adds bibliographic references to the MARC record.
    """
    if references:
        references_text = "Includes bibliographical references"
        if references_page_range:
            references_text += f" (p. {references_page_range})."
        record.add_field(Field(tag='504', indicators=[' ', ' '], subfields=[
            Subfield('a', references_text)
        ]))


def add_loc_subject_headings(record, loc_subject_1, loc_subject_2, loc_subject_3):
    """
    Adds LOC Subject Headings to the MARC record.
    """
    if loc_subject_1:
        record.add_field(Field(tag='650', indicators=[' ', '0'], subfields=[
            Subfield('a', loc_subject_1)
        ]))
    if loc_subject_2:
        record.add_field(Field(tag='650', indicators=[' ', '0'], subfields=[
            Subfield('a', loc_subject_2)
        ]))
    if loc_subject_3:
        record.add_field(Field(tag='650', indicators=[' ', '0'], subfields=[
            Subfield('a', loc_subject_3)
        ]))

def clean_filename(filename):
    """Remove any characters that are not alphanumeric, spaces, or underscores."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', filename).strip().replace(' ', '_')


def download_marc_record(marc_record, title, author, console_output):
    """
    Downloads the MARC record to a file.
    """
    default_filename = f"{clean_filename(author)}_{clean_filename(title)}.mrc"

    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(
        None, "Save MARC Record", default_filename, "MARC Files (*.mrc)", options=options
    )

    if save_path:
        try:
            with open(save_path, 'wb') as file:
                file.write(marc_record)
            console_output.append("MARC Record saved successfully.")
            console_output.append(f"Filename: {save_path}")
        except IOError as e:
            console_output.append(f"File I/O error: {str(e)}")
            QMessageBox.critical(
                None, "Error",
                "An error occurred during MARC record saving. See the log for details."
            )
