from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..db import Player, get_session
from ..auth import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new player account."""
    # Check if email already exists
    existing = session.exec(
        select(Player).where(Player.email == payload.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A player with this email already exists.",
        )
    
    # Create new player
    player = Player(
        name=payload.name,
        email=payload.email,
        wins=0,
        losses=0,
        points=0,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(player.id)})
    
    return TokenResponse(
        access_token=access_token,
        player={
            "id": player.id,
            "name": player.name,
            "email": player.email,
            "wins": player.wins,
            "losses": player.losses,
            "points": player.points,
        }
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    """Login with name and email."""
    # Find player by name and email
    player = session.exec(
        select(Player).where(
            Player.name == payload.name,
            Player.email == payload.email
        )
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No player found with that name and email combination.",
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(player.id)})
    
    return TokenResponse(
        access_token=access_token,
        player={
            "id": player.id,
            "name": player.name,
            "email": player.email,
            "wins": player.wins,
            "losses": player.losses,
            "points": player.points,
        }
    )

