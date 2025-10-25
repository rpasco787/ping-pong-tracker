# 🏓 Ping Pong Leaderboard

A full-stack web application for tracking ping pong matches and maintaining a competitive leaderboard. Built with FastAPI (backend) and Next.js (frontend).

## Features

- **Player Management**: Add and track players with optional email addresses
- **Match Recording**: Record matches with multiple games and automatic winner calculation
- **Live Leaderboard**: Real-time rankings based on points, wins, losses, and win rates
- **Match History**: View recent matches with detailed game scores
- **Dark Mode UI**: Modern, eye-friendly dark theme
- **REST API**: Clean FastAPI backend with automatic validation

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Compiler**: Optimized React rendering

## Project Structure

```
ping-pong-tracker/
├── backend/
│   ├── app/
│   │   ├── routers/          # API route handlers
│   │   │   ├── health.py     # Health check endpoint
│   │   │   ├── players.py    # Player CRUD operations
│   │   │   └── matches.py    # Match recording and retrieval
│   │   ├── schemas/          # Pydantic models
│   │   │   ├── players.py    # Player validation schemas
│   │   │   └── matches.py    # Match validation schemas
│   │   ├── store.py          # In-memory data storage
│   │   ├── config.py         # App configuration
│   │   └── main.py           # FastAPI app initialization
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main leaderboard page
│   │   │   ├── layout.tsx    # Root layout
│   │   │   └── globals.css   # Global styles
│   │   └── lib/
│   │       └── api.ts        # API client functions
│   └── package.json          # Node dependencies
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.12+** (for backend)
- **Node.js 18+** (for frontend)
- **npm** or **yarn** (for frontend package management)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The web app will be available at `http://localhost:3000`

## Usage

### Adding Players

1. Navigate to the "Add New Player" section
2. Enter player name (required) and email (optional)
3. Click "Add Player"

### Recording Matches

1. Click "Record New Match" (requires at least 2 players)
2. Select home and away players
3. Enter game scores (can add multiple games)
4. Click "Save Match"

The leaderboard will automatically update with new stats!

### Scoring System

- **Win**: 3 points
- **Loss**: 0 points
- Winner is determined by who wins the majority of games in a match

## API Endpoints

### Health
- `GET /healthz` - Health check

### Players
- `GET /api/players` - List all players (with optional search query)
- `POST /api/players` - Create a new player

### Matches
- `GET /api/matches` - List all matches (sorted by most recent)
- `POST /api/matches` - Record a new match

## Data Models

### Player
```typescript
{
  id: number
  name: string
  email?: string
  wins: number
  losses: number
  points: number
}
```

### Match
```typescript
{
  id: number
  played_at: string (ISO 8601)
  home_id: number
  away_id: number
  games: Array<{
    home: number
    away: number
  }>
}
```

## Development Notes

### In-Memory Storage
The current implementation uses in-memory storage, which means:
- ⚠️ Data resets when the backend server restarts
- 💡 Perfect for development and testing
- 🔄 For production, consider adding a database (PostgreSQL, MongoDB, etc.)

### CORS Configuration
The backend is configured to accept requests from `http://localhost:3000` (the Next.js dev server). Update `backend/app/config.py` if deploying to production.

## Future Enhancements

- [ ] Add persistent database (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Player profiles with avatars
- [ ] Advanced statistics (streaks, head-to-head records)
- [ ] Match scheduling and notifications
- [ ] Tournament bracket system
- [ ] Export data (CSV, PDF)
- [ ] Mobile responsive design improvements
- [ ] Real-time updates with WebSockets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with ❤️ for ping pong enthusiasts
- Inspired by competitive gaming leaderboards
- Powered by modern web technologies

---

**Happy Pinging and Ponging!** 🏓✨
