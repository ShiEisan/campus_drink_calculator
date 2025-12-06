# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Drink(db.Model):
    __tablename__ = "drinks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    brand = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)        # e.g., "中杯"
    calories = db.Column(db.Float, nullable=False)        # kcal
    sugar_grams = db.Column(db.Float, nullable=False)     # sugar g
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "size": self.size,
            "calories": self.calories,
            "sugar_grams": self.sugar_grams,
            "created_at": self.created_at.isoformat()
        }
