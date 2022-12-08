""""vmware_cloud_volumes"

Revision ID: ff5f881f5088
Revises: 34ea1c1bfe4c
Create Date: 2019-05-21 09:58:24.075537

Migration moved from bcd2ac6d3474

"""
from alembic import op
import sqlalchemy as sa
import logging
from mysql.connector.errors import ProgrammingError as MysqlProgrammingError
from sqlalchemy.exc import ProgrammingError as AlchemyProgrammingError

LOG = logging.getLogger(__name__)


# revision identifiers, used by Alembic.
revision = 'ff5f881f5088'
down_revision = '34ea1c1bfe4c'
branch_labels = None
depends_on = None

UPGRADE_ERRORS = [
    "Duplicate column name 'vmware_disk_file'",
    "Duplicate column name 'vmware_machine_id'"
]

DOWNGRADE_ERRORS = [
    "Can't DROP 'vmware_machine_id'; check that column/key exists",
    "Can't DROP 'vmware_disk_file'; check that column/key exists"
]


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.add_column('cloud_volume', sa.Column(
            'vmware_disk_file', sa.String(length=256), nullable=True))
        op.add_column('cloud_volume', sa.Column(
            'vmware_machine_id', sa.String(length=256), nullable=True))
    except (MysqlProgrammingError, AlchemyProgrammingError) as ex:
        if ex.orig.msg in UPGRADE_ERRORS:
            LOG.warning(ex.orig.msg)
            pass
        else:
            raise
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.drop_column('cloud_volume', 'vmware_machine_id')
        op.drop_column('cloud_volume', 'vmware_disk_file')
    except (MysqlProgrammingError, AlchemyProgrammingError) as ex:
        if ex.orig.msg in DOWNGRADE_ERRORS:
            LOG.warning(ex.orig.msg)
            pass
        else:
            raise
    # ### end Alembic commands ###
