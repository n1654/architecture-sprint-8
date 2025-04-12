from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import jwt
import logging
from functools import wraps
import pytz
import requests
from jwt.algorithms import RSAAlgorithm
from jwt import PyJWKClient

# LOGGING ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS CONFIG ------------------------------------------------------------------
CORS(app, resources={
    r"/reports": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
        "supports_credentials": True,
        "max_age": 86400
    }
})

# KEYCLOAK CONFIG --------------------------------------------------------------
KEYCLOAK_URL = "http://keycloak:8080/realms/reports-realm"
JWKS_URL = f"{KEYCLOAK_URL}/protocol/openid-connect/certs"
jwks_client = PyJWKClient(JWKS_URL)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Обработка OPTIONS-запроса для CORS
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split()[1]
        
        if not token:
            logger.warning("Token is missing")
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            logger.info(f"Trying to validate token with JWKS endpoint: {JWKS_URL}")
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            logger.info("Successfully retrieved signing key")
            
            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                # audience="reports-api" # "aud" claim disabled, otherwise keycloak config should be changed
            )

            logger.info(f"Token successfully decoded. Claims: {list(decoded_token.keys())}")
            logger.info(f"Token validated for user: {decoded_token.get('preferred_username', 'unknown')}")
        except jwt.PyJWKClientError as e:
            logger.error(f"JWKS client error: {str(e)}")
            logger.error(f"Keycloak JWKS endpoint: {JWKS_URL}")
            return jsonify({'message': 'Authentication service unavailable'}), 503
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            logger.error(f"Token validation error: ")
            return jsonify({'message': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/reports', methods=['GET', 'OPTIONS'])
@token_required
def generate_report():
    """
        SIMPLE REPORT GENERATES CURRENT TIMESTAMP
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    logger.info("Report generation requested")
    tz = pytz.timezone('Europe/Moscow')
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    report_message = f"Dummy report generated: {timestamp}"
    logger.info(f"Generated report: {report_message}")
    
    response = jsonify({"report": report_message})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    return response

if __name__ == '__main__':
    logger.info("Starting API server on port 8000")
    app.run(host='0.0.0.0', port=8000, debug=True)