"""
Cloud-Native Banking Application
Senior-Level Production Code
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger

# Initialize Flask App

app = Flask(__name__)
# ============= CONFIGURATION =============
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
'DATABASE_URL',
'postgresql://bankuser:bankpass@localhost:5432/banking_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
'pool_pre_ping': True,
'pool_recycle': 3600,
'pool_size': 10,
'max_overflow': 20,
'connect_args': {'connect_timeout': 10}
}
# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in
app.config['JWT_ALGORITHM'] = 'HS256'
# ============= LOGGING =============
def setup_logging():
"""Configure structured JSON logging"""
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
'%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.INFO)
setup_logging()
# ============= EXTENSIONS =============
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)
metrics = PrometheusMetrics(app)
# ============= IMPORT MODELS & ROUTES =============
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.routes import auth_bp, accounts_bp, transactions_bp
# ============= REGISTER BLUEPRINTS =============
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(accounts_bp, url_prefix='/api/v1/accounts')
app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
# ============= HEALTH CHECK ENDPOINTS =============
@app.route('/health', methods=['GET'])
def health_check():
"""Kubernetes liveness probe"""
try:
db.session.execute('SELECT 1')
return jsonify({
'status': 'healthy',
'timestamp': datetime.utcnow().isoformat(),
'service': 'banking-api'
}), 200
except Exception as e:
app.logger.error(f"Health check failed: {str(e)}")
return jsonify({
'status': 'unhealthy',
'error': str(e)
}), 500
@app.route('/ready', methods=['GET'])
def readiness_check():
"""Kubernetes readiness probe"""
try:
db.session.execute('SELECT 1')
return jsonify({'status': 'ready'}), 200
except Exception as e:
return jsonify({'status': 'not_ready', 'error': str(e)}), 503
@app.route('/info', methods=['GET'])
def info():
"""Application info endpoint"""
return jsonify({
'service': 'cloud-native-banking-api',
'version': os.getenv('APP_VERSION', '1.0.0'),
'environment': os.getenv('ENV', 'development'),
'timestamp': datetime.utcnow().isoformat()
}), 200
# ============= ERROR HANDLERS =============
@app.errorhandler(400)
def bad_request(error):
return jsonify({'error': 'Bad request'}), 400
@app.errorhandler(401)
def unauthorized(error):
return jsonify({'error': 'Unauthorized'}), 401
@app.errorhandler(403)
def forbidden(error):
return jsonify({'error': 'Forbidden'}), 403
@app.errorhandler(404)
def not_found(error):
return jsonify({'error': 'Not found'}), 404
@app.errorhandler(500)
def internal_error(error):
app.logger.error(f"Internal server error: {str(error)}")
db.session.rollback()
return jsonify({'error': 'Internal server error'}), 500
# ============= REQUEST/RESPONSE LOGGING =============
@app.before_request
def log_request():
app.logger.info(f"REQUEST: {request.method} {request.path} from {request.remote_
@app.after_request
def log_response(response):
app.logger.info(f"RESPONSE: {request.method} {request.path} - Status: {response.
return response
# ============= STARTUP & SHUTDOWN =============
@app.before_first_request
def create_tables():
"""Create database tables on startup"""
    db.create_all()
    app.logger.info("Database tables created/verified")
if __name__ == '__main__':
# Development only
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_ENV') == 'development'
)