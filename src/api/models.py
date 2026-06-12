from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from src.api.database import Base

class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    full_name = Column(String)
    is_active = Column(Boolean)

class PlayerGameStat(Base):
    __tablename__ = "player_game_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer)
    game_id = Column(String)
    game_date = Column(Date)
    season = Column(String)
    matchup = Column(String)
    home_away = Column(String)
    opponent_abbr = Column(String)
    minutes_played = Column(Float)
    points = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    fg_attempted = Column(Integer)
    fg_made = Column(Integer)
    fg3_attempted = Column(Integer)
    fg3_made = Column(Integer)
    ft_attempted = Column(Integer)
    ft_made = Column(Integer)
