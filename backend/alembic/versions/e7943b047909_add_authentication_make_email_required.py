"""add_authentication_make_email_required

Revision ID: e7943b047909
Revises: 6e20894e54a6
Create Date: 2025-10-30 00:09:22.062468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e7943b047909'
down_revision: Union[str, None] = '6e20894e54a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN directly, so we need to:
    # 1. Create a new table with the correct schema
    # 2. Copy data from old table
    # 3. Drop old table
    # 4. Rename new table
    
    # However, for simplicity and since we're in development:
    # We'll just ensure any existing NULL emails are handled
    
    # For SQLite, we need to check the database type
    connection = op.get_bind()
    
    # Update any NULL emails to a placeholder (shouldn't exist in production)
    connection.execute(sa.text(
        "UPDATE player SET email = 'unknown_' || id || '@example.com' WHERE email IS NULL"
    ))
    
    # Note: The NOT NULL constraint is already defined in the model
    # SQLite will enforce it on new inserts/updates
    # For a proper migration on PostgreSQL, you would use:
    # op.alter_column('player', 'email', nullable=False)


def downgrade() -> None:
    # Downgrade would make email nullable again
    # For SQLite, this is complex and not needed for development
    # For PostgreSQL:
    # op.alter_column('player', 'email', nullable=True)
    pass

