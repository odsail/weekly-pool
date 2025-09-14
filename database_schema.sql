-- NFL Confidence Pool Database Schema
-- SQLite database for storing picks, analysis, and team data

-- Teams table
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    abbreviation TEXT NOT NULL UNIQUE,
    conference TEXT NOT NULL,
    division TEXT NOT NULL
);

-- Games table
CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    season_year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    game_date TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    total_points INTEGER,
    margin INTEGER,
    winner_team_id INTEGER,
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id),
    FOREIGN KEY (winner_team_id) REFERENCES teams(id),
    UNIQUE(season_year, week, home_team_id, away_team_id)
);

-- Odds table
CREATE TABLE odds (
    id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL,
    bookmaker TEXT NOT NULL,
    home_ml INTEGER,
    away_ml INTEGER,
    total_points REAL,
    home_win_prob REAL,
    away_win_prob REAL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Picks table
CREATE TABLE picks (
    id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    pick_team_id INTEGER NOT NULL,
    confidence_points INTEGER NOT NULL,
    win_probability REAL NOT NULL,
    total_points_prediction INTEGER,
    is_correct BOOLEAN,
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (pick_team_id) REFERENCES teams(id)
);

-- Team performance table (weekly stats)
CREATE TABLE team_performance (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    games_played INTEGER DEFAULT 1,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    points_scored REAL,
    points_allowed REAL,
    point_differential REAL,
    win_percentage REAL,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(team_id, season_year, week)
);

-- Analysis results table
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    season_year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    overall_accuracy REAL,
    correct_picks INTEGER,
    total_picks INTEGER,
    avg_total_points_error REAL,
    blowouts_count INTEGER,
    close_games_count INTEGER,
    avg_margin REAL,
    analysis_date TEXT NOT NULL,
    UNIQUE(season_year, week)
);

-- Confidence accuracy table
CREATE TABLE confidence_accuracy (
    id INTEGER PRIMARY KEY,
    analysis_id INTEGER NOT NULL,
    confidence_points INTEGER NOT NULL,
    correct_picks INTEGER,
    total_picks INTEGER,
    accuracy REAL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id)
);

-- Game analysis table
CREATE TABLE game_analysis (
    id INTEGER PRIMARY KEY,
    analysis_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    pick_team_id INTEGER NOT NULL,
    actual_winner_id INTEGER,
    is_correct BOOLEAN,
    total_points_error REAL,
    margin REAL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id),
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (pick_team_id) REFERENCES teams(id),
    FOREIGN KEY (actual_winner_id) REFERENCES teams(id)
);

-- Indexes for better performance
CREATE INDEX idx_games_season_week ON games(season_year, week);
CREATE INDEX idx_picks_season_week ON picks(season_year, week);
CREATE INDEX idx_team_performance_team_season ON team_performance(team_id, season_year);
CREATE INDEX idx_odds_game_timestamp ON odds(game_id, timestamp);
CREATE INDEX idx_analysis_season_week ON analysis_results(season_year, week);
