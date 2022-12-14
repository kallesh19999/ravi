""""cs_detaching_state"

Revision ID: b498ff3be45a
Revises: 04e6e0e8e763
Create Date: 2018-06-26 17:13:16.367944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b498ff3be45a'
down_revision = '04e6e0e8e763'
branch_labels = None
depends_on = None
old_cs_states = sa.Enum('PENDING', 'CREATING', 'UPDATING', 'DELETING',
                        'RUNNING', 'ROLLING_BACK', 'ERROR')
new_cs_states = sa.Enum('PENDING', 'CREATING', 'UPDATING', 'DELETING',
                        'DETACHING', 'RUNNING', 'ROLLING_BACK', 'ERROR')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'cloudsite', 'state', existing_type=new_cs_states, nullable=True,
        existing_server_default=sa.text("'PENDING'"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    ct = sa.sql.table('cloudsite', sa.sql.column('state', new_cs_states))
    op.execute(ct.update().where(ct.c.state.in_(
        ['DETACHING'])).values(state='ERROR'))
    op.alter_column(
        'cloudsite', 'state', existing_type=old_cs_states, nullable=True,
        existing_server_default=sa.text("'PENDING'"))
    # ### end Alembic commands ###
