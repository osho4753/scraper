# Podminkomat

A platform that analyzes the Terms & Conditions (T&C) of online stores.

## Overview

This script is part of the solution for the Podminkomat project, a platform that analyzes the Terms & Conditions (T&C) of online stores.
The purpose of the script is to find, extract, and save the full text of the terms of service, starting only from the main page of the website (URL). It supports:

HTML documents,

PDF documents,

dynamic websites on various platforms.

## How to run

- Requires Python 3.8+, Chrome, and ChromeDriver

## Installation & Setup

1. Set dependencies:

```bash
   pip install -r requirements.txt
```

2. Start:

```bash
    python scraper.py https://www.alza.cz
```

4. Result:

- terms_and_conditions.txt — extracted and cleaned T&C text.

- terms_and_conditions.pdf — if a PDF document was found.

## Technologies used

# Library Purpose

- Selenium Browser emulation, working with JS, clicks
- BeautifulSoup Parsing HTML pages
- pdfminer.six Extracting text from PDFs
- argparse CLI interface
- requests Downloading PDF files

## How it works

1. Go to the home page.

2. Collect all <a> links.

3. Search by T&C keywords:

4. “obchodní podmínky”, “terms and conditions”, etc.

5. Detect HTML or PDF T&C:

6. If PDF is found, it is downloaded and processed.

7. If HTML is found, it is cleaned up and saved.

## Special cases and modal windows

Some websites display T&Cs in modal windows or as dynamically loaded blocks. In these cases, an experimental method is implemented in scraper_additional.py for an example:

# Example:

The Breuninger website displays T&Cs inside a print-only modal window:

1. window.print() is applied via Chrome DevTools Protocol (CDP).

2. The page is printed to PDF.

3. The PDF is processed and saved as text.

Limitations:

- Manual configuration for the website is required (e.g., cookies button — ID ‘onetrust-accept-btn-handler’).

- Only works on websites that support Page.printToPDF by button(onclick="window.print()").

- Therefore, a separate script has been implemented for a specific website so as not to disrupt or load the automated scraper at this stage.
