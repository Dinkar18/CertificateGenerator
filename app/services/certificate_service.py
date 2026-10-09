from sqlalchemy.orm import Session
from app.models.certificate import Certificate

def get_certificate(db: Session, certificate_id: str) -> Certificate:
    return db.query(Certificate).filter(Certificate.id == certificate_id).first()
