"""Add unique constraints to User username and email

Revision ID: ab343f5b62b7
Revises: 8fa43f0c0505
Create Date: 2025-10-28 23:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab343f5b62b7'
down_revision: Union[str, None] = '8fa43f0c0505'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER TABLE ADD CONSTRAINT directly
    # So we'll recreate the table with unique constraints
    # First, drop the existing table if it's empty (or backup data)
    op.execute("""
        CREATE TABLE user_new (
            id INTEGER NOT NULL,
            username VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN NOT NULL,
            is_superuser BOOLEAN NOT NULL,
            player_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(player_id) REFERENCES player (id),
            UNIQUE (username),
            UNIQUE (email)
        )
    """)
    
    # Copy data if any exists
    op.execute("""
        INSERT INTO user_new SELECT * FROM user
    """)
    
    # Drop old table and rename new one
    op.execute("DROP TABLE user")
    op.execute("ALTER TABLE user_new RENAME TO user")
    
    # Recreate indexes
    op.create_index('ix_user_email', 'user', ['email'], unique=False)
    op.create_index('ix_user_username', 'user', ['username'], unique=False)


def downgrade() -> None:
    # Reverse the process
    op.execute("""
        CREATE TABLE user_old (
            id INTEGER NOT NULL,
            username VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN NOT NULL,
            is_superuser BOOLEAN NOT NULL,
            player_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(player_id) REFERENCES player (id)
        )
    """)
    
    op.execute("""
        INSERT INTO user_old SELECT * FROM user
    """)
    
    op.execute("DROP TABLE user")
    op.execute("ALTER TABLE user_old RENAME TO user")
    
    op.create_index('ix_user_email', 'user', ['email'], unique=False)
    op.create_index('ix_user_username', 'user', ['username'], unique=False)
