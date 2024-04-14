# SevenDot MLB Odds Web Scraping Project

This project is designed to scrape MLB player odds information from the DraftKings Sportsbook website. It utilizes Selenium for web scraping to collect data on player betting odds, specifically focusing on 'Over/Under' odds for both batters and pitchers. The scraped data is structured and saved in a pandas DataFrame, and the entire scraping process is automated to run at 20-minute intervals.

## Project Overview

The goal of this project is to provide a robust tool for collecting real-time odds data, which could be used for analysis, betting insights, or data-driven decision-making in sports analytics. It is particularly focused on extracting detailed odds information about MLB players from one of the leading betting platforms, making the data easily accessible and actionable.

## Technologies Used

- **Python**: The core programming language used for the project.
- **Selenium**: A powerful tool for web scraping that interacts with web pages programmatically.
- **Pandas**: Used for data manipulation and storage of the scraped data.
- **Git**: For version control and managing updates to the project.

## Execution Plan

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- **Python 3**: Make sure Python 3 is installed on your machine. Download and install it from the [official Python website](https://www.python.org/downloads/).
- **Git**: Download and install Git from the [official Git website](https://git-scm.com/downloads).
- **Google Chrome**: Ensure that Google Chrome is installed on your system as the Selenium WebDriver will use it to scrape data. Download it from the [official Google Chrome website](https://www.google.com/chrome/).

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

## Additional Notes

- Ensure that your virtual environment is set up with the correct versions of Python and Selenium. Compatibility issues might arise with newer or outdated versions.
- The scraper is configured to handle web elements dynamically, which means it should maintain functionality even if minor changes occur on the DraftKings website. However, significant changes to the website structure may require adjustments to the scraping script.
- The application implements robust error handling mechanisms. If the browser is closed unexpectedly or the program is terminated during the scraping process, the system will catch these exceptions and provide friendly error messages to inform the user of what went wrong. 
