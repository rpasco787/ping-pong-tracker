# Ping Pong Leaderboard

## Project Description

A full-stack web application for tracking ping pong matches and maintaining a competitive leaderboard with user authentication and weekly archives.

## Features

- **User Authentication**: Secure login and registration system with JWT tokens
- **Player Management**: Add and track players with stats including wins, losses, and points
- **Match Recording**: Record matches with multiple games and automatic winner calculation
- **Live Leaderboard**: Real-time rankings based on points, wins, losses, and win rates
- **Weekly Archives**: Automatic weekly reset with historical leaderboard preservation
- **Match History**: View recent matches with detailed game scores
- **Dark Mode UI**: Modern, responsive interface with dark theme

## Technologies Used

### Backend
- **Python 3.12+**
- **FastAPI**: Modern Python web framework for REST API
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **SQLite**: Lightweight database
- **Uvicorn**: ASGI server
- **APScheduler**: Task scheduling for weekly resets
- **JWT**: Token-based authentication

### Frontend
- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **React**: UI library
- **Tailwind CSS**: Utility-first CSS framework
- **React Compiler**: Optimized React rendering
