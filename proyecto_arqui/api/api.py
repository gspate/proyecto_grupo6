from fastapi import FastAPI, HTTPException, Query, status
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, DateTime, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Configuración de la base de datos

# Ruta para acceder a la BDD desde un contenedor Docker
DATABASE_URL = "postgresql://gustavog.spate:panCONqueso123?@postgres:5432/football_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, unique=True, index=True)
    referee = Column(String)
    timezone = Column(String)
    date = Column(Date)
    timestamp = Column(Integer)
    status_long = Column(String)
    status_short = Column(String)
    status_elapsed = Column(Integer)
    league_id = Column(Integer)
    league_name = Column(String)
    league_country = Column(String)
    league_logo = Column(String)
    league_flag = Column(String)
    league_season = Column(Integer)
    league_round = Column(String)
    home_team_id = Column(Integer)
    home_team_name = Column(String)
    home_team_logo = Column(String)
    home_team_winner = Column(Boolean)
    away_team_id = Column(Integer)
    away_team_name = Column(String)
    away_team_logo = Column(String)
    away_team_winner = Column(Boolean)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    odds_id = Column(Integer, nullable=True)
    odds_name = Column(String, nullable=True)
    odds_home_value = Column(Float, nullable=True)
    odds_draw_value = Column(Float, nullable=True)
    odds_away_value = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

Base.metadata.create_all(bind=engine)

# Crear la instancia de FastAPI
app = FastAPI()

# Definir el modelo de datos para la API
class FixtureBase(BaseModel):
    fixture_id: int
    referee: Optional[str] = None
    timezone: Optional[str] = None
    date: Optional[datetime] = None
    timestamp: int
    status_long: Optional[str] = None
    status_short: Optional[str] = None
    status_elapsed: Optional[int] = None
    league_id: Optional[int] = None
    league_name: Optional[str] = None
    league_country: Optional[str] = None
    league_logo: Optional[str] = None
    league_flag: Optional[str] = None
    league_season: Optional[int] = None
    league_round: Optional[str] = None
    home_team_id: Optional[int] = None
    home_team_name: Optional[str] = None
    home_team_logo: Optional[str] = None
    home_team_winner: Optional[bool] = None
    away_team_id: Optional[int] = None
    away_team_name: Optional[str] = None
    away_team_logo: Optional[str] = None
    away_team_winner: Optional[bool] = None
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    odds_id: Optional[int] = None
    odds_name: Optional[str] = None
    odds_home_value: Optional[float] = None
    odds_draw_value: Optional[float] = None
    odds_away_value: Optional[float] = None
    last_updated: Optional[datetime] = None

# Endpoint para obtener la lista de fixtures con paginación (RF1 y RF3)
@app.get("/fixtures", response_model=List[FixtureBase])
def get_fixtures(
    page: int = Query(1, gt=0),
    count: int = Query(25, gt=0),
    home: Optional[str] = None,
    away: Optional[str] = None,
    date: Optional[datetime] = None,
):
    db = SessionLocal()
    try:
        # Calcular el offset para la paginación
        offset = (page - 1) * count
        query = db.query(Fixture)
        
        # Consulta con paginación
        if home:
            query = query.filter(Fixture.home_team_name.ilike(f"%{home}%"))
        if away:
            query = query.filter(Fixture.away_team_name.ilike(f"%{away}%"))
        if date:
            query = query.filter(Fixture.date >= date)
            query = query.filter(Fixture.status_short == "NS")
        fixtures = query.offset(offset).limit(count).all()
        return fixtures
    
    finally:
        db.close()

# Endpoint para obtener un fixture por su ID (RF2)
@app.get("/fixtures/{fixture_id}", response_model=FixtureBase)
def get_fixture_by_id(fixture_id: int):
    db = SessionLocal()
    try:
        fixture = db.query(Fixture).filter(Fixture.fixture_id == fixture_id).first()
        if fixture is None:
            raise HTTPException(status_code=404, detail="Fixture not found")
        return fixture
    finally:
        db.close()

# Endpoint para postear un nuevo fixture en la base de datos
@app.post("/fixtures", response_model=FixtureBase)
def create_fixture(fixture: FixtureBase):
    db = SessionLocal()
    try:
        new_fixture = Fixture(**fixture.dict())
        db.add(new_fixture)
        db.commit()
        db.refresh(new_fixture)
        return new_fixture
    finally:
        db.close()

# Endpoint para actualizar un fixture por su ID
@app.put("/fixtures/{fixture_id}", response_model=FixtureBase)
def update_fixture(fixture_id: int, fixture: FixtureBase):
    db = SessionLocal()
    try:
        fixture_to_update = db.query(Fixture).filter(Fixture.fixture_id == fixture_id).first()
        if fixture_to_update is None:
            raise HTTPException(status_code=404, detail="Fixture not found")
        for key, value in fixture.dict().items():
            setattr(fixture_to_update, key, value)
        db.commit()
        db.refresh(fixture_to_update)
        return fixture_to_update
    finally:
        db.close()

# Endpoint para borrar todos los fixtures de la base de datos (PARA DEBUGGEAR)
@app.delete("/fixtures", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_fixtures():
    db = SessionLocal()
    try:
        # Ejecutar la eliminación de todos los registros
        db.query(Fixture).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar fixtures: {e}")
    finally:
        db.close()



