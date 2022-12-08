""""untie_employee_from_bu"

Revision ID: 2b485ea622cf
Revises: 436019c61530
Create Date: 2020-03-24 06:40:09.172797

"""
from alembic import op
import sqlalchemy as sa
import uuid
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, insert

# revision identifiers, used by Alembic.
revision = '2b485ea622cf'
down_revision = '1ce691446242'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('employee_ibfk_2', 'employee', type_='foreignkey')
    op.drop_column('employee', 'business_unit_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee', sa.Column(
        'business_unit_id', sa.String(length=36), nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        budget_table = table('budget',
                             column('deleted_at', Integer),
                             column('id', String(36)),
                             column('created_at', Integer),
                             column('budget', Integer))
        dt = datetime.datetime.utcnow().timestamp()
        budget_id = str(uuid.uuid4())
        ins_stmt = insert(budget_table).values(
            deleted_at=dt,
            id=budget_id,
            created_at=dt,
            budget=0
        )
        session.execute(ins_stmt)
        partner_id = str(uuid.uuid4())
        partner_table = table('partner',
                              column('deleted_at', Integer),
                              column('id', String(36)),
                              column('created_at', Integer),
                              column('name', String(256)),
                              column('email', String(256)),
                              column('budget_id', String(36)),
                              )
        ins_stmt = insert(partner_table).values(
            deleted_at=dt,
            id=partner_id,
            created_at=dt,
            budget_id=budget_id,
            name='Hystax_migration_2b485ea622cf',
            email="support@hystax.com"
        )
        session.execute(ins_stmt)
        employee_table = table('employee',
                               column('id', String(36)),
                               column('business_unit_id', String(36))
                               )
        session.execute(sa.update(employee_table).values(
            business_unit_id=partner_id))
        session.commit()
    finally:
        session.close()
    op.create_foreign_key('employee_ibfk_2', 'employee', 'partner',
                          ['business_unit_id'], ['id'])
    # ### end Alembic commands ###
