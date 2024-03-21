from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.matchday import Matchday
from app.models.coaches import CoachesDB
from app.models.media import MediaDB
from app.models.players import Player
from app.models.stadiums import Stadiums
from app.models.standing import LeagueTable
from app.scrapers.standings.standing import save_to_db, get_league_table, delete_all_data
from app.database import SessionLocal
from fastapi import HTTPException
from app.models.news import News


router = APIRouter(
    prefix='/competitions',
    tags=['league_table']
)
templates=Jinja2Templates(directory='templates')
@router.get("/scrape")
async def scrape_and_save_to_db():
    db = SessionLocal()

    try:
        scraped_data = get_league_table()
        if not scraped_data:
            raise HTTPException(status_code=404, detail="League data not found")
        delete_all_data()
        save_to_db(scraped_data, db)
        return {"message": "Data scraped and saved successfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get('/leagues_standings_data')
def league_standings():
    db = SessionLocal()
    leaguetable = db.query(LeagueTable).all()
    db.close()
    return leaguetable

@router.get('/view')
def view_league_tables(request: Request):
    db = SessionLocal()
    league_table=db.query(LeagueTable).all()
    coaches=db.query(CoachesDB).all()
    media=db.query(MediaDB).all()
    stadium=db.query(Stadiums).all()
    players=db.query(Player).all()
    matchday= db.query(Matchday).all()
    news = db.query(News).all()

    return templates.TemplateResponse('standings.html', {
        'request': request,
        'league_table':league_table,
        'coaches':coaches,
        'media':media,
        'stadium':stadium,
        'matchday' : matchday,
        'players' : players,
        'news': news
    
    })
