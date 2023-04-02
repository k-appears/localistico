import enum

from sqlalchemy import Enum

from localistico.database import db


class Status(enum.Enum):
    submitted = 1
    completed = 2
    aborted = 3


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(50))
    lat = db.Column(db.Float(asdecimal=True))
    lon = db.Column(db.Float(asdecimal=True))
    address = db.Column(db.String)
    phone = db.Column(db.String(30))

    rating_comparison = db.Column(db.Float(asdecimal=True))

    circle_lat = db.Column(db.Float(asdecimal=True))
    circle_lon = db.Column(db.Float(asdecimal=True))
    circle_radius = db.Column(db.Float(asdecimal=True))

    status = db.Column(Enum(Status))
    error_message = db.Column(db.String(256))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def serialized(self):
        return {
            'id': self.id,
            'place_id': self.place_id,
            'lat': float(self.lat) if self.lat else None,
            'lon': float(self.lon) if self.lon else None,
            'address': self.address,
            'phone': self.phone,
            'circle_lat': float(self.circle_lat) if self.circle_lat else None,
            'circle_lon': float(self.circle_lon) if self.circle_lon else None,
            'circle_radius': float(self.circle_radius) if self.circle_radius else None,
            'status': self.status.name,
            'error_message': self.error_message,
        }
