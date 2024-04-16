import schedule
import logging
import argparse
from time import sleep
from selenium import webdriver
from pandas import DataFrame, concat
from selenium.webdriver.common.by import By
from datetime import datetime, timezone, timedelta
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec

# Configure error logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s', filename='scraper.log',
                    filemode='w')


# Function to check if the current betting category contains "Over/Under" odds
def is_valid_category(driver):
    try:
        table_head = driver.find_element(By.CLASS_NAME, 'sportsbook-table__head')
        if 'over' not in table_head.text.lower():
            return False
        return True
    except NoSuchElementException:
        return False


# Converts game times from string format to structured datetime format
def convert_time_format(time_str):
    now = datetime.now()
    parts = time_str.split()
    day_part = parts[0]
    time_part = parts[1]

    if day_part == "TOMORROW":
        target_date = now + timedelta(days=1)
    elif day_part == "TODAY":
        target_date = now
    else:
        return "Error: Date part must be 'TODAY' or 'TOMORROW'"

    target_time = datetime.strptime(time_part, '%I:%M%p')
    final_datetime = target_date.replace(hour=target_time.hour, minute=target_time.minute, second=0)
    formatted_time = final_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    formatted_date = final_datetime.strftime('%Y-%m-%d')
    return formatted_time, formatted_date


# Converts local time to UTC time
def local_to_utc(local_time_str):
    local_time = datetime.strptime(local_time_str, '%Y-%m-%dT%H:%M:%S')
    current_zone = datetime.now().astimezone().tzinfo
    local_time = local_time.replace(tzinfo=current_zone)
    utc_time = local_time.astimezone(timezone.utc)
    formatted_utc_time = utc_time.strftime('%Y-%m-%dT%H:%M:%S')
    return formatted_utc_time


# Extracts team names from a given event
def extract_team_name(event):
    team_name = event.find_element(By.CLASS_NAME, 'sportsbook-event-accordion__title-wrapper').text
    team_names = team_name.split('\n')
    return team_names[0], team_names[-1]


# Extracts betting data from a single row in the odds table
def extract_event_data(row):
    player_name = row.find_element(By.CLASS_NAME, 'sportsbook-row-name').text
    td_elements = row.find_elements(By.TAG_NAME, 'td')

    data_entries = []
    for td in td_elements:
        if td.find_elements(By.CLASS_NAME, 'sportsbook-empty-cell'):
            # Sometimes the cell is empty
            odds_type = ''
            over_under_total = ''
            odds = ''
        else:
            odds_type = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__label').text
            over_under_total = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__line').text
            odds = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__elements').text

        data_entries.append({
            'player_name': player_name,
            'over_under_total': over_under_total,
            'odds_type': odds_type,
            'odds': odds
        })
    return data_entries


# Creates data rows for each player and event
def create_data_rows(game_time_utc, game_time_local, game_date, main_category_type, sub_category_type, home_team,
                     away_team, event_data):
    data_rows = []
    for data in event_data:
        data_row = {
            'time_now_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'time_now_local': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'game_time_utc': game_time_utc,
            'game_time_local': game_time_local,
            'game_date': game_date,
            'main_category_type': main_category_type,
            'sub_category_type': sub_category_type,
            'home_team': home_team,
            'away_team': away_team,
            **data
        }
        data_rows.append(data_row)
    return DataFrame(data_rows)


# Scrapes data from a subcategory if valid
def scrape_sub_category(driver, main_category, sub_category):
    all_data_frames = []
    if not is_valid_category(driver):
        print(f"{sub_category} does not have Over or Under odds. Skipping this sub category.")
        return DataFrame()

    main_category_type = main_category
    sub_category_type = sub_category

    events = driver.find_elements(By.CLASS_NAME, 'sportsbook-event-accordion__wrapper')
    for event in events:
        game_time_str = event.find_element(By.CLASS_NAME, 'sportsbook-event-accordion__date').text
        game_time_local, game_date = convert_time_format(game_time_str)
        game_time_utc = local_to_utc(game_time_local)

        away_team, home_team = extract_team_name(event)

        data_div = event.find_element(By.CLASS_NAME, 'sportsbook-table__body')
        rows = data_div.find_elements(By.TAG_NAME, 'tr')

        for row in rows:
            event_data = extract_event_data(row)
            data_frame = create_data_rows(game_time_utc, game_time_local, game_date, main_category_type,
                                          sub_category_type, home_team, away_team, event_data)
            all_data_frames.append(data_frame)

    return concat(all_data_frames, ignore_index=True)


# Continues to click through subcategories and scrape data under the main category
def scrape_main_category(driver, result, category):
    continue_clicking = True
    print(f"Starting to scrape main category: {category}")

    while continue_clicking:
        try:
            selected_link = driver.find_element(By.CSS_SELECTOR,
                                                "a.sportsbook-tabbed-subheader__tab-link[aria-selected='true']")
            main_category = category
            sub_category = selected_link.text
            print(f"Now scraping sub category: {sub_category}")
            sub_category_data = scrape_sub_category(driver, main_category, sub_category)
            result = concat([result, sub_category_data], ignore_index=True)

            next_link = selected_link.find_element(By.XPATH, "following-sibling::a[@aria-selected='false']")
            next_link.click()

            WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.CLASS_NAME, 'sportsbook-event-accordion__wrapper'))
            )

        except NoSuchElementException:
            continue_clicking = False
    return result


# Sets up the scraper to run at specified intervals
def run_scrape(headless=False):
    websites = ['https://sportsbook.draftkings.com/leagues/baseball/mlb?category=batter-props',
                'https://sportsbook.draftkings.com/leagues/baseball/mlb?category=pitcher-props']
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    result = DataFrame()

    try:
        for website in websites:
            driver.get(website)
            category = 'Batter Props' if 'batter-props' in website else 'Pitcher Props'
            if not driver.find_elements(By.XPATH, "//div[contains(text(), '" + category + "')]"):
                print(f"The main category '{category}' is currently not available.")
                continue

            category = category.upper()
            result = scrape_main_category(driver, result, category)

        result.to_csv('result.csv', index=False)
        print("This scraping session is complete. Please check the results in result.csv."
              "The next scrape will occur in 20 minutes.")

    except WebDriverException as e:
        logging.error(f"Web driver encountered an issue: {e}")
        print("An error occurred, please check scraper.log for details.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print("An error occurred, please check scraper.log for details.")
    finally:
        driver.quit()


# Schedules the scraper function to run periodically
def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--headless', action='store_true')
        args = parser.parse_args()

        run_scrape(headless=args.headless)
        schedule.every(20).minutes.do(lambda: run_scrape(headless=args.headless))
        while True:
            schedule.run_pending()
            sleep(1)
    except KeyboardInterrupt:
        print("Program has been interrupted by the user.")


if __name__ == "__main__":
    main()
