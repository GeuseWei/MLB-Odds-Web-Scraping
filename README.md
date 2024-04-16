# SevenDot MLB Odds Web Scraping Project

## Project Overview
This project is designed to scrape MLB player odds information from the DraftKings Sportsbook website. It utilizes Selenium for web scraping to collect data on player betting odds, specifically focusing on 'Over/Under' odds for both batters and pitchers. The scraped data is structured and saved in a pandas DataFrame, and the entire scraping process is automated to run at 20-minute intervals.

## Technologies Used

- **Python**: The core programming language used for the project.
- **Selenium**: A powerful tool for web scraping that interacts with web pages programmatically.
- **Pandas**: Used for data manipulation and storage of the scraped data.
- **Git**: For version control and managing updates to the project.

## Execution Plan

1. **Initialization**: Set up Selenium WebDriver and configure logging for error tracking.
2. **Category Selection**: Navigate to specific categories on the DraftKings website and begin data extraction.
3. **Data Extraction**: Verify categories, extract game times, team names, and player odds, and aggregate into a DataFrame.
4. **Looping Through Categories**: Use a `while` loop to navigate and scrape data from all relevant subcategories by simulating clicks on subsequent tabs.
5. **Scheduling**: Automate scraping to run at 20-minute intervals using the `schedule` library.
6. **Error Handling**: Log exceptions to `scraper.log` and provide concise console messages for quick checks.
7. **Shutdown**: Ensure proper closure of WebDriver sessions.
8. **User Interruption**: Handle `KeyboardInterrupt` for graceful shutdown.
## Setup Instructions

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

To run the scraper in head mode (default):

```bash
python main.py
```

To run the scraper in headless mode:

```bash
python main.py --headless
```

The program will execute every 20 minutes, scraping data and saving it to the result.csv file.

### Exiting the Virtual Environment

When you're finished working or need to deactivate the virtual environment, you can type:

```bash
deactivate
```

### Debugging
If you encounter issues during the execution of the program, please refer to the `scraper.log`  file for detailed error information. This log captures all errors and is the first place to look for understanding any issues that arise. 

## Additional Notes

- **Browser Visibility**: If you are not running in headless mode, please ensure that the browser window is at the forefront during scraping to guarantee data integrity.

- **Empty Data Cells**: Occasionally, the website may have empty cells where odds information is typically stored. The program is designed to handle these cases effectively, and corresponding entries in the DataFrame will be set as empty.

- **Missing Categories**: Sometimes, the 'Batter Props' and 'Pitcher Props' categories may temporarily be absent due to updates on the website. The program recognizes this situation and will report it in the command line output.
