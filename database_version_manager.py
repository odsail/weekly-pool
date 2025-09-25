#!/usr/bin/env python3
"""
Database version manager for NFL confidence pool system.
Handles database versioning and migration between versions.
"""
import os
import shutil
from typing import Optional
from database_manager import DatabaseManager

class DatabaseVersionManager:
    """Manages database versions and migrations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.current_version = self._get_current_version()
    
    def _get_current_version(self) -> str:
        """Get the current database version"""
        if os.path.exists(f"{self.data_dir}/nfl_pool_v2.db"):
            return "v2"
        elif os.path.exists(f"{self.data_dir}/nfl_pool_v1.db"):
            return "v1"
        elif os.path.exists(f"{self.data_dir}/nfl_pool.db"):
            return "v1"  # Legacy v1
        else:
            return "none"
    
    def get_database_path(self, version: Optional[str] = None) -> str:
        """Get the database path for a specific version"""
        if version is None:
            version = self.current_version
        
        if version == "v2":
            return f"{self.data_dir}/nfl_pool_v2.db"
        elif version == "v1":
            return f"{self.data_dir}/nfl_pool_v1.db"
        else:
            return f"{self.data_dir}/nfl_pool.db"
    
    def create_v2_database(self) -> bool:
        """Create a new v2 database with enhanced schema"""
        print("🔄 Creating v2 database with enhanced schema...")
        
        try:
            # Create new v2 database
            v2_path = self.get_database_path("v2")
            db_manager = DatabaseManager(db_path=v2_path)
            
            # Migrate data from v1 if it exists
            if self.current_version == "v1":
                print("📦 Migrating data from v1 to v2...")
                self._migrate_v1_to_v2()
            
            # Update current version
            self.current_version = "v2"
            
            print("✅ v2 database created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating v2 database: {e}")
            return False
    
    def _migrate_v1_to_v2(self):
        """Migrate data from v1 to v2 database"""
        v1_path = self.get_database_path("v1")
        v2_path = self.get_database_path("v2")
        
        if not os.path.exists(v1_path):
            print("⚠️  No v1 database found to migrate")
            return
        
        try:
            # Create v2 database manager
            v2_db = DatabaseManager(db_path=v2_path)
            
            # Import data from v1
            import sqlite3
            
            # Connect to both databases
            v1_conn = sqlite3.connect(v1_path)
            v2_conn = sqlite3.connect(v2_path)
            
            # Migrate teams (should be identical)
            v1_conn.execute("ATTACH DATABASE ? AS v2", (v2_path,))
            v1_conn.execute("INSERT OR IGNORE INTO v2.teams SELECT * FROM teams")
            v1_conn.commit()
            
            # Migrate games (add new columns with defaults)
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.games 
                (id, season_year, week, home_team_id, away_team_id, game_date, 
                 home_score, away_score, total_points, margin, winner_team_id, is_completed)
                SELECT id, season_year, week, home_team_id, away_team_id, game_date,
                       home_score, away_score, total_points, margin, winner_team_id, is_completed
                FROM games
            """)
            v1_conn.commit()
            
            # Migrate picks
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.picks 
                SELECT * FROM picks
            """)
            v1_conn.commit()
            
            # Migrate odds
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.odds 
                SELECT * FROM odds
            """)
            v1_conn.commit()
            
            # Migrate team performance
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.team_performance 
                SELECT * FROM team_performance
            """)
            v1_conn.commit()
            
            # Migrate analysis results
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.analysis_results 
                SELECT * FROM analysis_results
            """)
            v1_conn.commit()
            
            # Migrate confidence accuracy
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.confidence_accuracy 
                SELECT * FROM confidence_accuracy
            """)
            v1_conn.commit()
            
            # Migrate game analysis
            v1_conn.execute("""
                INSERT OR IGNORE INTO v2.game_analysis 
                SELECT * FROM game_analysis
            """)
            v1_conn.commit()
            
            v1_conn.close()
            v2_conn.close()
            
            print("✅ Data migration completed")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
    
    def get_database_info(self) -> dict:
        """Get information about all database versions"""
        info = {
            "current_version": self.current_version,
            "databases": {}
        }
        
        # Check v1 database
        v1_path = self.get_database_path("v1")
        if os.path.exists(v1_path):
            info["databases"]["v1"] = self._get_database_stats(v1_path)
        
        # Check v2 database
        v2_path = self.get_database_path("v2")
        if os.path.exists(v2_path):
            info["databases"]["v2"] = self._get_database_stats(v2_path)
        
        # Check legacy database
        legacy_path = f"{self.data_dir}/nfl_pool.db"
        if os.path.exists(legacy_path):
            info["databases"]["legacy"] = self._get_database_stats(legacy_path)
        
        return info
    
    def _get_database_stats(self, db_path: str) -> dict:
        """Get statistics for a database"""
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Get table counts
            tables = ['teams', 'games', 'picks', 'odds', 'team_performance', 
                     'analysis_results', 'confidence_accuracy', 'game_analysis',
                     'home_field_advantage', 'international_games']
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                except:
                    stats[table] = "N/A"
            
            # Get file size
            stats["file_size_mb"] = round(os.path.getsize(db_path) / (1024 * 1024), 2)
            
            conn.close()
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    def switch_to_version(self, version: str) -> bool:
        """Switch to a specific database version"""
        if version not in ["v1", "v2"]:
            print(f"❌ Invalid version: {version}")
            return False
        
        target_path = self.get_database_path(version)
        if not os.path.exists(target_path):
            print(f"❌ Version {version} database not found")
            return False
        
        # Update current version
        self.current_version = version
        print(f"✅ Switched to database version {version}")
        return True

def main():
    """Database version management CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage NFL pool database versions")
    parser.add_argument("--create-v2", action="store_true", help="Create v2 database")
    parser.add_argument("--info", action="store_true", help="Show database info")
    parser.add_argument("--switch", choices=["v1", "v2"], help="Switch to version")
    
    args = parser.parse_args()
    
    manager = DatabaseVersionManager()
    
    if args.create_v2:
        manager.create_v2_database()
    elif args.info:
        info = manager.get_database_info()
        print("📊 Database Version Information:")
        print(f"   Current Version: {info['current_version']}")
        print("\n📁 Available Databases:")
        for version, stats in info["databases"].items():
            print(f"   {version.upper()}:")
            for key, value in stats.items():
                if key != "error":
                    print(f"     {key}: {value}")
    elif args.switch:
        manager.switch_to_version(args.switch)
    else:
        print("Use --help for available options")

if __name__ == "__main__":
    main()






