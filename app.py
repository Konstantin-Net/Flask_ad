from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import atexit

"""Создание базе данных в PostgreSQL"""

DATABASE_URI = 'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(DATABASE_URI.format(
    username='postgres',
    password='admin',
    host='localhost',
    port=5432,
    database='app'
))

if not database_exists(engine.url):
    create_database(engine.url)

"""Создание таблицы в базе данных"""

Base = declarative_base()


class Ad(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    owner = Column(String(50), nullable=False)

    def __repr__(self):
        return '<Ad %r>' % self.title


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
atexit.register(engine.dispose)  # Встроенные в python обработчик, даём команду закрытие соединения с базой


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


""" REST API Flask для сайта объявлений"""


@app.route('/ads', methods=['POST'])
def create_ad():
    title = request.json['title']
    description = request.json['description']
    owner = request.json['owner']
    ad = Ad(title=title, description=description, owner=owner)
    db.session.add(ad)
    db.session.commit()
    return jsonify({'message': 'Ad created successfully'})


@app.route('/ads/<ad_id>', methods=['GET'])
def get_ad(ad_id):
    with Session() as session:
        ad = session.query(Ad).get(ad_id)
        if not ad:
            return jsonify({'message': 'Ad not found'})
        return jsonify({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'date_create': ad.date_created,
            'owner': ad.owner
        })


@app.route('/ads/<ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    with Session() as session:
        ad = session.query(Ad).get(ad_id)
        if not ad:
            return jsonify({'message': 'Ad not found'})
        session.delete(ad)
        session.commit()
        return jsonify({'message': 'Ad deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
