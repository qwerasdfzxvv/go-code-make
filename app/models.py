from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app import db


class COLUMNS(Model):
    __tablename__ = 'COLUMNS'
    __bind_key__ = 'information_schema'
    __table_args__ = (
        PrimaryKeyConstraint('table_schema', 'table_name'),
    )
    # id = Column(Integer, primary_key=True)
    table_schema = Column(String(64))
    table_name = Column(String(64))
    column_name = Column(String(64))
    ordinal_position= Column(Integer)
    is_nullable = Column(String(3))
    data_type = Column(String(64))



    def __repr__(self):
        return self.table_name

