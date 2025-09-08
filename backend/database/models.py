from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Region(db.Model):
    """Model for storing region information"""
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    area = db.Column(db.Float)  # Area in square kilometers
    coordinates = db.Column(db.Text)  # JSON string with coordinates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deforestation_data = db.relationship('DeforestationData', backref='region', lazy=True)
    reports = db.relationship('Report', backref='region', lazy=True)
    
    def __repr__(self):
        return f'<Region {self.name}>'
    
    def to_dict(self):
        """Convert region to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'area': self.area,
            'coordinates': self.coordinates,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DeforestationData(db.Model):
    """Model for storing deforestation data"""
    __tablename__ = 'deforestation_data'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    forest_area = db.Column(db.Float, nullable=False)  # Forest area in hectares
    deforested_area = db.Column(db.Float, nullable=False)  # Deforested area in hectares
    percentage_change = db.Column(db.Float, default=0.0)  # Percentage change from previous period
    severity = db.Column(db.String(20), default='low')  # Severity level: low, medium, high
    coordinates = db.Column(db.Text)  # JSON string with coordinates
    image_path = db.Column(db.String(255))  # Path to the satellite image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeforestationData {self.id} - {self.date}>'
    
    def to_dict(self):
        """Convert deforestation data to dictionary"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'region_name': self.region.name if self.region else None,
            'date': self.date.isoformat(),
            'forest_area': self.forest_area,
            'deforested_area': self.deforested_area,
            'percentage_change': self.percentage_change,
            'severity': self.severity,
            'coordinates': self.coordinates,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }

class Report(db.Model):
    """Model for storing generated reports"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    report_type = db.Column(db.String(50), nullable=False)  # summary, detailed, prediction, impact
    title = db.Column(db.String(255))
    data = db.Column(db.Text)  # JSON string with report data
    file_path = db.Column(db.String(255))  # Path to the generated report file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.id} - {self.report_type}>'
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'region_name': self.region.name if self.region else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'report_type': self.report_type,
            'title': self.title,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    """Model for storing user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Alert(db.Model):
    """Model for storing deforestation alerts"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    coordinates = db.Column(db.Text)  # JSON string with coordinates
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    region = db.relationship('Region', backref='alerts')
    resolver = db.relationship('User', backref='resolved_alerts')
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.title}>'
    
    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'region_name': self.region.name if self.region else None,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'coordinates': self.coordinates,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolver.username if self.resolver else None,
            'created_at': self.created_at.isoformat()
        }

class ApiKey(db.Model):
    """Model for storing API keys"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='api_keys')
    
    def __repr__(self):
        return f'<ApiKey {self.name}>'
    
    def to_dict(self):
        """Convert API key to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class AuditLog(db.Model):
    """Model for storing audit logs"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text)  # JSON string with additional details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }