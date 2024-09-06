# MARC Record Tool

The **MARC Record Tool** is a GUI-based application for cataloging, searching, and scraping MARC records. Designed for librarians and researchers, this tool simplifies the process of working with MARC records by offering an intuitive interface for creating, editing, and exporting bibliographic information.

## Table of Contents

- [Features](#features)
- [Application Overview](#application-overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Original Cataloging Tab](#original-cataloging-tab)
  - [Search Libraries Tab](#search-libraries-tab)
  - [Scrape MARC Tab](#scrape-marc-tab)
- [Functionality Details](#functionality-details)
  - [Creating a MARC Record](#creating-a-marc-record)
  - [Searching Libraries](#searching-libraries)
  - [Scraping MARC Records](#scraping-marc-records)
- [Help and Support](#help-and-support)
- [Contributing](#contributing)

## Features

- **Original Cataloging**: Create MARC records by manually inputting bibliographic data.
- **Search Libraries**: Query multiple libraries by ISBN, title, and author to retrieve MARC records.
- **Scrape MARC Records**: Extract MARC records from specific URLs.
- **Export and Download MARC**: Save MARC records in various formats after creation or retrieval.
- **Library Management**: Add, edit, and manage library URLs for custom searches.

## Application Overview

### Main Window

The application is divided into three main tabs:

1. **Original Cataloging**: For creating new MARC records from scratch.
2. **Search Libraries**: For searching multiple libraries for MARC records based on ISBN, title, or author.
3. **Scrape MARC**: For scraping MARC records from a provided URL.

Here is a screenshot of the main application interface:

![Screenshot 2024-09-06 013016](https://github.com/user-attachments/assets/ffbb4825-5da7-49c2-9af3-a96cde091464)
*The main interface of the MARC Record Tool, featuring the Original Cataloging tab.*

## Installation

### Prerequisites

- Python 3.x
- PyQt5 (for the GUI)
- Required Python libraries (install via `requirements.txt`):

```bash
pip install -r requirements.txt
```

### Clone the Repository

Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/jspann21/MARC_Record_Tool.git
cd MARC_Record_Tool
```

## Usage

Run the application by executing `main.py`:

```bash
python main.py
```

### Original Cataloging Tab

The **Original Cataloging** tab allows you to create new MARC records by entering bibliographic details such as title, author, publisher, and more.

![Screenshot 2024-09-06 013016](https://github.com/user-attachments/assets/06cd571f-bd9c-4a7c-b4e6-e5a8287edbff)
*Enter bibliographic information, create MARC records, and download them.*

### Search Libraries Tab

In the **Search Libraries** tab, users can search for MARC records across multiple libraries by entering an ISBN, title, or author. Users can also add or edit the list of searchable libraries.

![Screenshot 2024-09-06 013025](https://github.com/user-attachments/assets/07099ea6-fe52-41e2-ad2d-af06d459e85e)
*Search for MARC records across multiple libraries using ISBN or title and author.*

### Scrape MARC Tab

The **Scrape MARC** tab allows users to scrape MARC records from a provided URL.

![Screenshot 2024-09-06 013031](https://github.com/user-attachments/assets/aefe1b02-b111-4500-bf5a-1cdbbf28f47a)
*Scrape MARC records directly from a URL.*

## Functionality Details

### Creating a MARC Record

1. In the **Original Cataloging** tab, enter as much information as possible into the provided fields.
2. Click **Create MARC** to generate the MARC record.
3. Click **Download MARC** to save the created MARC record to your local machine.

### Searching Libraries

1. Navigate to the **Search Libraries** tab. The libraries listed have downloadable MARC records.
2. Enter an ISBN, title, or author to search for matching MARC records in the listed libraries.
3. Click **ISBN search** or **Title & Author search** to begin the search.
4. The **Status** indicates if a record is Found or Not Found. Click on the **Status** to go to the MARC record link.

You can also manage libraries by adding new libraries with their search URLs.

### Scraping MARC Records

1. Go to the **Scrape MARC** tab.
2. Enter the URL containing the MARC record to be scraped.
3. Click **Scrape URL** to extract the MARC record and save it.

## Help and Support

Click the **Help** button in the top-right corner of the application window to get detailed instructions for using the tool. A pop-up window will provide information on how to use each feature.

## Contributing

If you find any issues or have suggestions for improvement, feel free to open a pull request or file an issue on GitHub. Contributions are welcome!
