import requests
from bs4 import BeautifulSoup
from app.database import SessionLocal
from app.models.form import FormDB
from sqlalchemy import delete

teams = ['almeria']


def scrape_form_in_last_matches():
    games_data = []

    for team in teams:
        url = f"https://www.besoccer.com/team/{team}"

        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')

        game_elements = soup.find_all('a', class_='spree-box')
        try:
            team_name = soup.find('h2', class_='title ta-c').text.strip()
        except AttributeError:
            team_name = "Team Name Not Found"  # Provide a default value

        for game_element in game_elements:
            enemy_logo_element = game_element.find('img', class_='shield')
            competition_element = game_element.find('img', class_='league')
            result_element = game_element.find('div', class_='result')
            result_1 = game_element.find('div', class_='result mb5')
            if enemy_logo_element and competition_element and result_element:
                enemy_logo = enemy_logo_element['src']

                competition_logo = competition_element['src']
                for result in result_1:
                    first_span = result_element.find('span')
                    if first_span.find('b'):
                        h_or_a = 'H'
                    else:
                        h_or_a = 'A'

                result = result_element.find_all('span')
                if len(result) >= 2:
                    home_scores = result[0].text.strip()
                    away_scores = result[1].text.strip()
                else:
                    home_scores = "N/A"
                    away_scores = "N/A"

                date_element = game_element.find('div', class_='date')
                date = date_element.text.strip() if date_element else "N/A"

                game_data = {
                    "team_name": team_name,
                    "enemy_logo": enemy_logo,
                    "competition_logo": competition_logo,
                    "date": date,
                    "home_scores": home_scores,
                    "away_scores": away_scores,
                    "h_or_a": h_or_a,
                }

                games_data.append(game_data)

    return games_data

def delete_all_games(session):

    session.execute(delete(FormDB))
    session.commit()

def insert_data_into_database(games_data):
    session = SessionLocal()
    delete_all_games(session)

    try:
        if games_data:
            for entry in games_data:
                form_db = FormDB(**entry)
                session.add(form_db)
            session.commit()

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
