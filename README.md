# SevenDot MLB Odds Web Scraping Project

This project scrapes MLB player odds information from the DraftKings Sportsbook website using Selenium. The scraper is set to run at a regular interval and saves the results to a pandas dataframe.

## Quick Start

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

Make sure you have Python 3 and git installed on your machine. You can download and install the appropriate version of Python for your operating system from the official [Python website](https://www.python.org/downloads/). Git can be downloaded and installed from the official [Git website](https://git-scm.com/downloads).

### Installation

First, clone the Git repository to your local machine:

```bash
git clone https://github.com/GeuseWei/MLB-Odds-Web-Scraping.git
cd MLB-Odds-Web-Scraping
```

Next, create a Python virtual environment and activate it:

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Running the Code

To run the scraper:

```bash
python main.py
```

The program will execute every 20 minutes, scraping data and saving it to the result.csv file.

### Exiting the Virtual Environment

When you're finished working or need to deactivate the virtual environment, you can type:

```bash
deactivate
```
