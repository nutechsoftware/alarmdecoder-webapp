"""New cameras table.

Revision ID: 279107daa1ff
Revises: 4a5a64ce67ac
Create Date: 2015-05-12 15:57:01.895157

"""

# revision identifiers, used by Alembic.
revision = '279107daa1ff'
down_revision = '4a5a64ce67ac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    try:
        op.drop_table('cameras')
    except sa.exc.OperationalError:
        pass

    op.create_table('cameras',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=32), nullable=False),
    sa.Column('username', sa.VARCHAR(length=32)),
    sa.Column('password', sa.VARCHAR(length=255)),
    sa.Column('get_jpg_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )   

def downgrade():
    op.drop_table('cameras')
