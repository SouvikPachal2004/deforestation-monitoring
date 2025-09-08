from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json

from api.routes import api
from models.deforestation_model import DeforestationModel
from models.satellite_image_processor import SatelliteImageProcessor
from utils.data_analysis import DataAnalyzer
from utils.time_series import TimeSeriesAnalyzer
from database.models import db, DeforestationData, Region, Report

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///deforestation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize extensions
db.init_app(app)
CORS(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# Initialize models and processors
deforestation_model = DeforestationModel()
image_processor = SatelliteImageProcessor()
data_analyzer = DataAnalyzer()
time_series_analyzer = TimeSeriesAnalyzer()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')

@app.route('/analysis')
def analysis():
    """Render the analysis page"""
    return render_template('analysis.html')

@app.route('/reports')
def reports():
    """Render the reports page"""
    return render_template('reports.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Render the contact page"""
    return render_template('contact.html')

@app.route('/api/deforestation-data', methods=['GET'])
def get_deforestation_data():
    """API endpoint to get deforestation data"""
    try:
        region_id = request.args.get('region_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Query the database based on parameters
        query = DeforestationData.query
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        if start_date:
            query = query.filter(DeforestationData.date >= start_date)
        
        if end_date:
            query = query.filter(DeforestationData.date <= end_date)
        
        data = query.all()
        
        # Convert to JSON-serializable format
        result = [{
            'id': item.id,
            'region_id': item.region_id,
            'region_name': item.region.name if item.region else None,
            'date': item.date.isoformat(),
            'forest_area': item.forest_area,
            'deforested_area': item.deforested_area,
            'percentage_change': item.percentage_change,
            'severity': item.severity,
            'coordinates': json.loads(item.coordinates) if item.coordinates else None
        } for item in data]
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """API endpoint to get all regions"""
    try:
        regions = Region.query.all()
        
        result = [{
            'id': region.id,
            'name': region.name,
            'description': region.description,
            'area': region.area,
            'coordinates': json.loads(region.coordinates) if region.coordinates else None
        } for region in regions]
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to upload satellite images"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No selected file'
            }), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image
            region_id = request.form.get('region_id')
            date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Analyze the image for deforestation
            analysis_result = image_processor.analyze_image(filepath)
            
            # Save results to database
            region = Region.query.get(region_id) if region_id else None
            
            deforestation_data = DeforestationData(
                region_id=region_id,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                forest_area=analysis_result['forest_area'],
                deforested_area=analysis_result['deforested_area'],
                percentage_change=analysis_result['percentage_change'],
                severity=analysis_result['severity'],
                coordinates=json.dumps(analysis_result['coordinates'])
            )
            
            db.session.add(deforestation_data)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'id': deforestation_data.id,
                    'filename': filename,
                    'analysis_result': analysis_result
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_images():
    """API endpoint to analyze uploaded images"""
    try:
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        region_id = data.get('region_id')
        analysis_type = data.get('analysis_type', 'deforestation')
        
        if not image_ids:
            return jsonify({
                'success': False,
                'error': 'No images provided'
            }), 400
        
        # Get image paths
        image_paths = []
        for image_id in image_ids:
            # In a real implementation, you would get the file path from the database
            # For now, we'll assume the image is in the upload folder
            image_paths.append(os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}.png"))
        
        # Analyze images based on type
        if analysis_type == 'deforestation':
            result = deforestation_model.detect_deforestation(image_paths)
        elif analysis_type == 'regrowth':
            result = deforestation_model.detect_regrowth(image_paths)
        elif analysis_type == 'health':
            result = deforestation_model.assess_forest_health(image_paths)
        elif analysis_type == 'fire':
            result = deforestation_model.detect_fire_damage(image_paths)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Perform time series analysis if multiple images
        if len(image_paths) > 1:
            time_series_result = time_series_analyzer.analyze_trend(result)
            result['time_series'] = time_series_result
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """API endpoint to generate deforestation reports"""
    try:
        data = request.get_json()
        region_id = data.get('region_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type', 'summary')
        
        # Get deforestation data for the report
        query = DeforestationData.query
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        if start_date:
            query = query.filter(DeforestationData.date >= start_date)
        
        if end_date:
            query = query.filter(DeforestationData.date <= end_date)
        
        deforestation_data = query.all()
        
        if not deforestation_data:
            return jsonify({
                'success': False,
                'error': 'No data found for the specified parameters'
            }), 404
        
        # Generate report based on type
        if report_type == 'summary':
            report_data = data_analyzer.generate_summary_report(deforestation_data)
        elif report_type == 'detailed':
            report_data = data_analyzer.generate_detailed_report(deforestation_data)
        elif report_type == 'prediction':
            report_data = data_analyzer.generate_prediction_report(deforestation_data)
        elif report_type == 'impact':
            report_data = data_analyzer.generate_impact_report(deforestation_data)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid report type'
            }), 400
        
        # Save report to database
        region = Region.query.get(region_id) if region_id else None
        
        report = Report(
            region_id=region_id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            report_type=report_type,
            data=json.dumps(report_data)
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'report_id': report.id,
                'report_data': report_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """API endpoint to get reports"""
    try:
        region_id = request.args.get('region_id')
        report_type = request.args.get('report_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        query = Report.query
        
        if region_id:
            query = query.filter(Report.region_id == region_id)
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        # Paginate results
        reports = query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'reports': [{
                'id': report.id,
                'region_id': report.region_id,
                'region_name': report.region.name if report.region else None,
                'start_date': report.start_date.isoformat() if report.start_date else None,
                'end_date': report.end_date.isoformat() if report.end_date else None,
                'report_type': report.report_type,
                'created_at': report.created_at.isoformat(),
                'file_url': f"/api/reports/{report.id}/download"
            } for report in reports.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': reports.total,
                'pages': reports.pages
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports/<int:report_id>/download', methods=['GET'])
def download_report(report_id):
    """API endpoint to download a report"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Generate the report file
        report_data = json.loads(report.data)
        
        # In a real implementation, you would generate a PDF, Excel, or other file format
        # For now, we'll return a JSON file
        filename = f"report_{report.id}_{report.report_type}.json"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """API endpoint to handle contact form submissions"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([name, email, subject, message]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        # In a real implementation, you would save this to the database and/or send an email
        # For now, we'll just return a success response
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/newsletter', methods=['POST'])
def newsletter_subscribe():
    """API endpoint to handle newsletter subscriptions"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # In a real implementation, you would save this to the database and/or add to a mailing list
        # For now, we'll just return a success response
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to newsletter'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'geojson'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)