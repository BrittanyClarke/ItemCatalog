#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create basketball category

category1 = Category(name='Basketball')

session.add(category1)
session.commit()

# Create basketball items

categoryItem1 = CategoryItem(name='Goal Rim',
                             description="""2-pointer, 3-pointer,
                             you can have them all with this
                             CLASSIC basketball rim.
                             You can't have basketball without
                             the rim for the ball to go into.
                             We only use the best metal in the
                             bizz for this rim.""",
                             category=category1)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name='Goal Net',
                             description="""SWISH! SWOOSH!
                             Ooh, nothing feels as good
                             as sinking an all-net shot.
                             This netting is made of quality
                             cotton. It is weather-resistant and
                             perfect for outdoor or indoor use!""",
                             category=category1)
session.add(categoryItem2)
session.commit()

# Create softball category

category2 = Category(name='Softball')

session.add(category2)
session.commit()

# Create softball items

categoryItem1 = CategoryItem(name='Metal Bat',
                             description="""CLINK! Nothing feels
                             quite as good as hitting a pop-fly
                             out to the outfield with this
                             awesome metal bat.""",
                             category=category2)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name='Batting Gloves',
                             description="""Sure, hitting a
                             softball feels good after a
                             tricky pitch, but you know what
                             doesn't feel so great? The
                             vibrations from that hit into your
                             hands, ouch! Avoid some of this with
                             these nice, leather batting gloves!
                             Not to mention, they make you look pretty cool.""",
                             category=category2)
session.add(categoryItem2)
session.commit()

# Create soccer category

category3 = Category(name='Soccer')

session.add(category3)
session.commit()

# Create soccer items

categoryItem1 = CategoryItem(name='Soccer Ball',
                             description="Can't play soccer without a ball!",
                             category=category3)
session.add(categoryItem1)
session.commit()

items = session.query(CategoryItem).all()
for item in items:
    print item.name
