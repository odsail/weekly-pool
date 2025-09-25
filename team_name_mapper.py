#!/usr/bin/env python3
"""
Team name mapper for handling historical team name changes and variations.
Maps old team names to current standardized names.
"""

class TeamNameMapper:
    """Maps historical team names to current standardized names"""
    
    def __init__(self):
        # Historical team name mappings
        self.team_mappings = {
            # Washington team name changes
            'Washington': 'Washington Commanders',
            'Washington Redskins': 'Washington Commanders',
            'Washington Football Team': 'Washington Commanders',
            
            # Oakland Raiders moved to Las Vegas
            'Oakland Raiders': 'Las Vegas Raiders',
            
            # Pro Bowl/All-Star games (should be filtered out)
            'AFC All-Stars': None,
            'NFC All-Stars': None,
            'AFC': None,
            'NFC': None,
            
            # Other potential variations
            'Los Angeles Chargers': 'Los Angeles Chargers',  # Already correct
            'Los Angeles Rams': 'Los Angeles Rams',  # Already correct
        }
        
        # Current NFL teams (32 teams)
        self.current_teams = {
            'Arizona Cardinals': {'abbreviation': 'ARI', 'conference': 'NFC', 'division': 'West'},
            'Atlanta Falcons': {'abbreviation': 'ATL', 'conference': 'NFC', 'division': 'South'},
            'Baltimore Ravens': {'abbreviation': 'BAL', 'conference': 'AFC', 'division': 'North'},
            'Buffalo Bills': {'abbreviation': 'BUF', 'conference': 'AFC', 'division': 'East'},
            'Carolina Panthers': {'abbreviation': 'CAR', 'conference': 'NFC', 'division': 'South'},
            'Chicago Bears': {'abbreviation': 'CHI', 'conference': 'NFC', 'division': 'North'},
            'Cincinnati Bengals': {'abbreviation': 'CIN', 'conference': 'AFC', 'division': 'North'},
            'Cleveland Browns': {'abbreviation': 'CLE', 'conference': 'AFC', 'division': 'North'},
            'Dallas Cowboys': {'abbreviation': 'DAL', 'conference': 'NFC', 'division': 'East'},
            'Denver Broncos': {'abbreviation': 'DEN', 'conference': 'AFC', 'division': 'West'},
            'Detroit Lions': {'abbreviation': 'DET', 'conference': 'NFC', 'division': 'North'},
            'Green Bay Packers': {'abbreviation': 'GB', 'conference': 'NFC', 'division': 'North'},
            'Houston Texans': {'abbreviation': 'HOU', 'conference': 'AFC', 'division': 'South'},
            'Indianapolis Colts': {'abbreviation': 'IND', 'conference': 'AFC', 'division': 'South'},
            'Jacksonville Jaguars': {'abbreviation': 'JAX', 'conference': 'AFC', 'division': 'South'},
            'Kansas City Chiefs': {'abbreviation': 'KC', 'conference': 'AFC', 'division': 'West'},
            'Las Vegas Raiders': {'abbreviation': 'LV', 'conference': 'AFC', 'division': 'West'},
            'Los Angeles Chargers': {'abbreviation': 'LAC', 'conference': 'AFC', 'division': 'West'},
            'Los Angeles Rams': {'abbreviation': 'LAR', 'conference': 'NFC', 'division': 'West'},
            'Miami Dolphins': {'abbreviation': 'MIA', 'conference': 'AFC', 'division': 'East'},
            'Minnesota Vikings': {'abbreviation': 'MIN', 'conference': 'NFC', 'division': 'North'},
            'New England Patriots': {'abbreviation': 'NE', 'conference': 'AFC', 'division': 'East'},
            'New Orleans Saints': {'abbreviation': 'NO', 'conference': 'NFC', 'division': 'South'},
            'New York Giants': {'abbreviation': 'NYG', 'conference': 'NFC', 'division': 'East'},
            'New York Jets': {'abbreviation': 'NYJ', 'conference': 'AFC', 'division': 'East'},
            'Philadelphia Eagles': {'abbreviation': 'PHI', 'conference': 'NFC', 'division': 'East'},
            'Pittsburgh Steelers': {'abbreviation': 'PIT', 'conference': 'AFC', 'division': 'North'},
            'San Francisco 49ers': {'abbreviation': 'SF', 'conference': 'NFC', 'division': 'West'},
            'Seattle Seahawks': {'abbreviation': 'SEA', 'conference': 'NFC', 'division': 'West'},
            'Tampa Bay Buccaneers': {'abbreviation': 'TB', 'conference': 'NFC', 'division': 'South'},
            'Tennessee Titans': {'abbreviation': 'TEN', 'conference': 'AFC', 'division': 'South'},
            'Washington Commanders': {'abbreviation': 'WSH', 'conference': 'NFC', 'division': 'East'},
        }
    
    def map_team_name(self, team_name: str) -> str:
        """Map historical team name to current standardized name"""
        if not team_name:
            return None
            
        # Check direct mapping first
        if team_name in self.team_mappings:
            return self.team_mappings[team_name]
        
        # If it's already a current team name, return as-is
        if team_name in self.current_teams:
            return team_name
        
        # Try case-insensitive matching
        team_name_lower = team_name.lower()
        for current_team in self.current_teams.keys():
            if current_team.lower() == team_name_lower:
                return current_team
        
        # If no mapping found, return original (might be a new team or error)
        return team_name
    
    def is_valid_team(self, team_name: str) -> bool:
        """Check if team name is valid (not Pro Bowl, etc.)"""
        mapped_name = self.map_team_name(team_name)
        return mapped_name is not None and mapped_name in self.current_teams
    
    def get_team_info(self, team_name: str) -> dict:
        """Get team information (abbreviation, conference, division)"""
        mapped_name = self.map_team_name(team_name)
        if mapped_name and mapped_name in self.current_teams:
            return self.current_teams[mapped_name]
        return None
    
    def should_skip_game(self, home_team: str, away_team: str) -> bool:
        """Check if game should be skipped (Pro Bowl, etc.)"""
        return not self.is_valid_team(home_team) or not self.is_valid_team(away_team)

def main():
    """Test the team name mapper"""
    mapper = TeamNameMapper()
    
    # Test cases
    test_teams = [
        'Washington',
        'Washington Redskins', 
        'Oakland Raiders',
        'AFC All-Stars',
        'NFC All-Stars',
        'Las Vegas Raiders',
        'Kansas City Chiefs'
    ]
    
    print("🧪 Testing team name mapper:")
    for team in test_teams:
        mapped = mapper.map_team_name(team)
        valid = mapper.is_valid_team(team)
        info = mapper.get_team_info(team)
        print(f"  '{team}' -> '{mapped}' (Valid: {valid})")
        if info:
            print(f"    Info: {info}")

if __name__ == '__main__':
    main()






