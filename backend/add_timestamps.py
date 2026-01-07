from sqlalchemy import text
from database import SessionLocal, engine
from datetime import datetime

def add_timestamp_columns():
    """Add created_at and updated_at columns to the participants table"""
    
    db = SessionLocal()
    
    try:
        # Check if columns already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='participants' 
            AND column_name IN ('created_at', 'updated_at')
        """)).fetchall()
        
        existing_columns = [row[0] for row in result]
        
        # Add created_at column if it doesn't exist
        if 'created_at' not in existing_columns:
            print("Adding created_at column...")
            db.execute(text("""
                ALTER TABLE participants 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            
        # Add updated_at column if it doesn't exist
        if 'updated_at' not in existing_columns:
            print("Adding updated_at column...")
            db.execute(text("""
                ALTER TABLE participants 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            
        # Update existing records with realistic timestamps if columns were just added
        if 'created_at' not in existing_columns or 'updated_at' not in existing_columns:
            print("Updating existing records with timestamps...")
            
            # Get all participant IDs
            participants = db.execute(text("SELECT id FROM participants ORDER BY id")).fetchall()
            
            # Update each participant with realistic timestamps
            base_time = datetime.utcnow()
            for i, (participant_id,) in enumerate(participants):
                created_time = base_time - timedelta(days=30-i*2)  # Spread over 30 days
                updated_time = base_time - timedelta(minutes=i*10)  # Recent updates
                
                db.execute(text("""
                    UPDATE participants 
                    SET created_at = :created_at, updated_at = :updated_at 
                    WHERE id = :id
                """), {
                    'created_at': created_time,
                    'updated_at': updated_time,
                    'id': participant_id
                })
        
        db.commit()
        print("Timestamp columns added successfully!")
        
    except Exception as e:
        print(f"Error adding timestamp columns: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import timedelta
    add_timestamp_columns()