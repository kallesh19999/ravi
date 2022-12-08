""""changed_conn_string_type"

Revision ID: 6b7f641658d1
Revises: bdd2c6f1942c
Create Date: 2016-12-29 17:16:57.722931

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6b7f641658d1'
down_revision = 'bdd2c6f1942c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('failover', sa.Column('connection_string', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('failover', 'connection_string')
    # ### end Alembic commands ###
