#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):

    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    
    @property
    def serialize(self):
        return {'name': self.name, 'id': self.id}


class CategoryItem(Base):

    __tablename__ = 'category_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)

    description = Column(String(250))

    category_id = Column(Integer, ForeignKey('category.id'))

    category = relationship(Category)

    creation_date = Column(DateTime)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {'name': self.name, 'id': self.id,
                'description': self.description}

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
