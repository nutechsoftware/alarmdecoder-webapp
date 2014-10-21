"""Added event_log timestamp index.

Revision ID: 2d5cbdadf755
Revises: 2d1953265871
Create Date: 2014-10-21 12:10:01.562548

"""

# revision identifiers, used by Alembic.
revision = '2d5cbdadf755'
down_revision = '2d1953265871'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('ix_event_log_timestamp', 'event_log', ['timestamp'])

def downgrade():
    op.drop_index('ix_event_log_timestamp')
