class BaseRepository:
    """Repositorio base con operaciones CRUD genéricas"""
    
    def __init__(self, model_class, session):
        self.model_class = model_class
        self.session = session
    
    def get_by_id(self, record_id):
        return self.model_class.query.get(record_id)
    
    def get_all(self):
        return self.model_class.query.all()
    
    def create(self, **kwargs):
        instance = self.model_class(**kwargs)
        from app.factories.app_factory import db
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def delete(self, instance):
        from app.factories.app_factory import db
        db.session.delete(instance)
        db.session.commit()
