import schedule
from time import sleep
from selenium import webdriver
from pandas import DataFrame, concat
from selenium.webdriver.common.by import By
from datetime import datetime, timezone, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def is_valid_category(driver):
    try:
        table_head = driver.find_element(By.CLASS_NAME, 'sportsbook-table__head')
        if 'over' not in table_head.text.lower():
            return False
        return True
    except NoSuchElementException:
        return False


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


def local_to_utc(local_time_str):
    local_time = datetime.strptime(local_time_str, '%Y-%m-%dT%H:%M:%S')
    current_zone = datetime.now().astimezone().tzinfo
    local_time = local_time.replace(tzinfo=current_zone)
    utc_time = local_time.astimezone(timezone.utc)
    formatted_utc_time = utc_time.strftime('%Y-%m-%dT%H:%M:%S')
    return formatted_utc_time


def extract_team_name(event):
    team_name = event.find_element(By.CLASS_NAME, 'sportsbook-event-accordion__title-wrapper').text
    team_names = team_name.split('\n')
    return team_names[0], team_names[-1]


def extract_event_data(row):
    player_name = row.find_element(By.CLASS_NAME, 'sportsbook-row-name').text
    td_elements = row.find_elements(By.TAG_NAME, 'td')

    data_entries = []
    for td in td_elements:
        odds_type = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__label').text
        over_under_total = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__line').text
        odds = td.find_element(By.CLASS_NAME, 'sportsbook-outcome-cell__elements').text
        data_entries.append({
            'player_name': player_name,
            'odds_type': odds_type,
            'over_under_total': over_under_total,
            'odds': odds
        })
    return data_entries


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


def scrape_sub_category(driver, main_category, sub_category):
    all_data_frames = []
    if not is_valid_category(driver):
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


def scrape_main_category(driver, result, category):
    continue_clicking = True

    while continue_clicking:
        try:
            selected_link = driver.find_element(By.CSS_SELECTOR,
                                                "a.sportsbook-tabbed-subheader__tab-link[aria-selected='true']")
            main_category = category
            sub_category = selected_link.text
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


def run_scrape():
    websites = ['https://sportsbook.draftkings.com/leagues/baseball/mlb?category=batter-props',
                'https://sportsbook.draftkings.com/leagues/baseball/mlb?category=pitcher-props']

    driver = webdriver.Chrome()
    result = DataFrame()

    for website in websites:
        driver.get(website)
        category = 'BATTER PROPS' if 'batter-props' in website else 'PITCHER PROPS'
        result = scrape_main_category(driver, result, category)

    result.to_csv('result.csv', index=False)
    driver.quit()


def main():
    run_scrape()
    schedule.every(20).minutes.do(run_scrape)
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == "__main__":
    main()
