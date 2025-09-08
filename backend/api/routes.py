from flask import Blueprint, request, jsonify, current_app
from models.deforestation_model import DeforestationModel
from models.satellite_image_processor import SatelliteImageProcessor
from utils.data_analysis import DataAnalyzer
from utils.time_series import TimeSeriesAnalyzer
from database.models import db, DeforestationData, Region, Report
import os
import json
from datetime import datetime
import uuid

api = Blueprint('api', __name__)

# Initialize models and processors
deforestation_model = DeforestationModel()
image_processor = SatelliteImageProcessor()
data_analyzer = DataAnalyzer()
time_series_analyzer = TimeSeriesAnalyzer()

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@api.route('/deforestation-stats', methods=['GET'])
def get_deforestation_stats():
    """Get overall deforestation statistics"""
    try:
        # Get query parameters
        region_id = request.args.get('region_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Query the database
        query = DeforestationData.query
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        if start_date:
            query = query.filter(DeforestationData.date >= start_date)
        
        if end_date:
            query = query.filter(DeforestationData.date <= end_date)
        
        data = query.all()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data found for the specified parameters'
            }), 404
        
        # Calculate statistics
        total_area = sum(item.forest_area + item.deforested_area for item in data)
        total_forest_area = sum(item.forest_area for item in data)
        total_deforested_area = sum(item.deforested_area for item in data)
        
        # Calculate percentages
        forest_percentage = (total_forest_area / total_area) * 100 if total_area > 0 else 0
        deforested_percentage = (total_deforested_area / total_area) * 100 if total_area > 0 else 0
        
        # Calculate average percentage change
        avg_percentage_change = sum(item.percentage_change for item in data) / len(data) if data else 0
        
        # Determine severity based on deforestation percentage
        if deforested_percentage > 20:
            severity = "high"
        elif deforested_percentage > 10:
            severity = "medium"
        else:
            severity = "low"
        
        # Get region name if region_id is provided
        region_name = None
        if region_id:
            region = Region.query.get(region_id)
            if region:
                region_name = region.name
        
        return jsonify({
            'success': True,
            'data': {
                'region_id': region_id,
                'region_name': region_name,
                'start_date': start_date,
                'end_date': end_date,
                'total_area': total_area,
                'total_forest_area': total_forest_area,
                'total_deforested_area': total_deforested_area,
                'forest_percentage': forest_percentage,
                'deforested_percentage': deforested_percentage,
                'avg_percentage_change': avg_percentage_change,
                'severity': severity,
                'data_points': len(data)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/deforestation-hotspots', methods=['GET'])
def get_deforestation_hotspots():
    """Get deforestation hotspots"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 10))
        severity = request.args.get('severity')
        
        # Query the database for high deforestation areas
        query = DeforestationData.query.filter(DeforestationData.deforested_area > 0)
        
        if severity:
            query = query.filter(DeforestationData.severity == severity)
        
        # Order by deforested area (descending) and limit results
        hotspots = query.order_by(DeforestationData.deforested_area.desc()).limit(limit).all()
        
        # Convert to JSON-serializable format
        result = []
        for hotspot in hotspots:
            coordinates = None
            if hotspot.coordinates:
                try:
                    coordinates = json.loads(hotspot.coordinates)
                except:
                    pass
            
            result.append({
                'id': hotspot.id,
                'region_id': hotspot.region_id,
                'region_name': hotspot.region.name if hotspot.region else None,
                'date': hotspot.date.isoformat(),
                'forest_area': hotspot.forest_area,
                'deforested_area': hotspot.deforested_area,
                'percentage_change': hotspot.percentage_change,
                'severity': hotspot.severity,
                'coordinates': coordinates
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/time-series', methods=['GET'])
def get_time_series_data():
    """Get time series data for deforestation"""
    try:
        # Get query parameters
        region_id = request.args.get('region_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Query the database
        query = DeforestationData.query
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        if start_date:
            query = query.filter(DeforestationData.date >= start_date)
        
        if end_date:
            query = query.filter(DeforestationData.date <= end_date)
        
        # Order by date
        data = query.order_by(DeforestationData.date).all()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data found for the specified parameters'
            }), 404
        
        # Extract time series data
        dates = [item.date.isoformat() for item in data]
        forest_areas = [item.forest_area for item in data]
        deforested_areas = [item.deforested_area for item in data]
        percentage_changes = [item.percentage_change for item in data]
        
        # Calculate trends
        forest_trend = time_series_analyzer.calculate_trend(forest_areas)
        deforestation_trend = time_series_analyzer.calculate_trend(deforested_areas)
        
        # Get region name if region_id is provided
        region_name = None
        if region_id:
            region = Region.query.get(region_id)
            if region:
                region_name = region.name
        
        return jsonify({
            'success': True,
            'data': {
                'region_id': region_id,
                'region_name': region_name,
                'start_date': start_date,
                'end_date': end_date,
                'dates': dates,
                'forest_areas': forest_areas,
                'deforested_areas': deforested_areas,
                'percentage_changes': percentage_changes,
                'trends': {
                    'forest': forest_trend,
                    'deforestation': deforestation_trend
                },
                'data_points': len(data)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/predict', methods=['POST'])
def predict_deforestation():
    """Predict future deforestation based on historical data"""
    try:
        data = request.get_json()
        region_id = data.get('region_id')
        periods = int(data.get('periods', 12))  # Number of periods to predict
        
        if not region_id:
            return jsonify({
                'success': False,
                'error': 'Region ID is required'
            }), 400
        
        # Get historical data for the region
        historical_data = DeforestationData.query.filter_by(region_id=region_id).order_by(DeforestationData.date).all()
        
        if not historical_data:
            return jsonify({
                'success': False,
                'error': 'No historical data found for the specified region'
            }), 404
        
        # Extract time series data
        dates = [item.date for item in historical_data]
        forest_areas = [item.forest_area for item in historical_data]
        deforested_areas = [item.deforested_area for item in historical_data]
        
        # Make predictions
        forest_prediction = time_series_analyzer.predict(forest_areas, periods)
        deforestation_prediction = time_series_analyzer.predict(deforested_areas, periods)
        
        # Generate future dates
        last_date = dates[-1]
        future_dates = []
        for i in range(1, periods + 1):
            # This is a simplified approach - in a real implementation, you would handle different time intervals
            future_date = datetime(last_date.year, last_date.month, 1)
            future_date = future_date.replace(month=(future_date.month + i - 1) % 12 + 1, 
                                           year=future_date.year + (future_date.month + i - 1) // 12)
            future_dates.append(future_date.isoformat())
        
        # Get region name
        region = Region.query.get(region_id)
        region_name = region.name if region else None
        
        return jsonify({
            'success': True,
            'data': {
                'region_id': region_id,
                'region_name': region_name,
                'historical_data': {
                    'dates': [date.isoformat() for date in dates],
                    'forest_areas': forest_areas,
                    'deforested_areas': deforested_areas
                },
                'prediction': {
                    'dates': future_dates,
                    'forest_areas': forest_prediction,
                    'deforested_areas': deforestation_prediction
                },
                'summary': {
                    'current_forest_area': forest_areas[-1],
                    'current_deforested_area': deforested_areas[-1],
                    'predicted_forest_area': forest_prediction[-1],
                    'predicted_deforested_area': deforestation_prediction[-1],
                    'predicted_forest_loss': forest_areas[-1] - forest_prediction[-1],
                    'predicted_deforestation_increase': deforestation_prediction[-1] - deforested_areas[-1]
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/regions', methods=['POST'])
def create_region():
    """Create a new region"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        area = data.get('area')
        coordinates = data.get('coordinates')
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Region name is required'
            }), 400
        
        # Create new region
        region = Region(
            name=name,
            description=description,
            area=area,
            coordinates=json.dumps(coordinates) if coordinates else None
        )
        
        db.session.add(region)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': region.id,
                'name': region.name,
                'description': region.description,
                'area': region.area,
                'coordinates': json.loads(region.coordinates) if region.coordinates else None,
                'created_at': region.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/regions/<int:region_id>', methods=['PUT'])
def update_region(region_id):
    """Update a region"""
    try:
        region = Region.query.get_or_404(region_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            region.name = data['name']
        if 'description' in data:
            region.description = data['description']
        if 'area' in data:
            region.area = data['area']
        if 'coordinates' in data:
            region.coordinates = json.dumps(data['coordinates'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': region.id,
                'name': region.name,
                'description': region.description,
                'area': region.area,
                'coordinates': json.loads(region.coordinates) if region.coordinates else None,
                'updated_at': region.updated_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/regions/<int:region_id>', methods=['DELETE'])
def delete_region(region_id):
    """Delete a region"""
    try:
        region = Region.query.get_or_404(region_id)
        
        # Check if there's associated data
        associated_data = DeforestationData.query.filter_by(region_id=region_id).first()
        if associated_data:
            return jsonify({
                'success': False,
                'error': 'Cannot delete region with associated deforestation data'
            }), 400
        
        db.session.delete(region)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Region deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/alerts', methods=['GET'])
def get_alerts():
    """Get deforestation alerts"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 20))
        severity = request.args.get('severity')
        region_id = request.args.get('region_id')
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        
        # In a real implementation, you would have an Alert model
        # For now, we'll simulate alerts from deforestation data
        query = DeforestationData.query.filter(DeforestationData.deforested_area > 0)
        
        if severity:
            query = query.filter(DeforestationData.severity == severity)
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        # Order by date (descending) and limit results
        alerts = query.order_by(DeforestationData.date.desc()).limit(limit).all()
        
        # Convert to alert format
        result = []
        for alert in alerts:
            coordinates = None
            if alert.coordinates:
                try:
                    coordinates = json.loads(alert.coordinates)
                except:
                    pass
            
            result.append({
                'id': f"alert-{alert.id}",
                'region_id': alert.region_id,
                'region_name': alert.region.name if alert.region else None,
                'date': alert.date.isoformat(),
                'severity': alert.severity,
                'deforested_area': alert.deforested_area,
                'percentage_change': alert.percentage_change,
                'coordinates': coordinates,
                'resolved': resolved,
                'message': f"Deforestation detected in {alert.region.name if alert.region else 'unknown region'}: {alert.deforested_area} hectares lost"
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Mark an alert as resolved"""
    try:
        # In a real implementation, you would update the Alert model
        # For now, we'll just return a success response
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} marked as resolved'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get data for the dashboard"""
    try:
        # Get overall statistics
        total_regions = Region.query.count()
        total_data_points = DeforestationData.query.count()
        
        # Get latest data point
        latest_data = DeforestationData.query.order_by(DeforestationData.date.desc()).first()
        
        # Calculate total forest and deforested areas
        total_forest_area = db.session.query(db.func.sum(DeforestationData.forest_area)).scalar() or 0
        total_deforested_area = db.session.query(db.func.sum(DeforestationData.deforested_area)).scalar() or 0
        
        # Get recent alerts (high severity deforestation)
        recent_alerts = DeforestationData.query.filter(
            DeforestationData.severity == 'high'
        ).order_by(DeforestationData.date.desc()).limit(5).all()
        
        # Get top regions by deforestation
        top_regions = db.session.query(
            Region.name,
            db.func.sum(DeforestationData.deforested_area).label('total_deforested')
        ).join(
            DeforestationData, Region.id == DeforestationData.region_id
        ).group_by(
            Region.name
        ).order_by(
            db.func.sum(DeforestationData.deforested_area).desc()
        ).limit(5).all()
        
        # Format data for response
        dashboard_data = {
            'stats': {
                'total_regions': total_regions,
                'total_data_points': total_data_points,
                'total_forest_area': total_forest_area,
                'total_deforested_area': total_deforested_area
            },
            'latest_data': {
                'date': latest_data.date.isoformat() if latest_data else None,
                'forest_area': latest_data.forest_area if latest_data else 0,
                'deforested_area': latest_data.deforested_area if latest_data else 0,
                'percentage_change': latest_data.percentage_change if latest_data else 0,
                'severity': latest_data.severity if latest_data else None
            },
            'recent_alerts': [
                {
                    'id': f"alert-{alert.id}",
                    'region_name': alert.region.name if alert.region else None,
                    'date': alert.date.isoformat(),
                    'severity': alert.severity,
                    'deforested_area': alert.deforested_area,
                    'percentage_change': alert.percentage_change
                }
                for alert in recent_alerts
            ],
            'top_regions': [
                {
                    'name': region.name,
                    'total_deforested': region.total_deforested
                }
                for region in top_regions
            ]
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/export-data', methods=['GET'])
def export_data():
    """Export deforestation data in various formats"""
    try:
        # Get query parameters
        format_type = request.args.get('format', 'json')
        region_id = request.args.get('region_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Query the database
        query = DeforestationData.query
        
        if region_id:
            query = query.filter(DeforestationData.region_id == region_id)
        
        if start_date:
            query = query.filter(DeforestationData.date >= start_date)
        
        if end_date:
            query = query.filter(DeforestationData.date <= end_date)
        
        data = query.all()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data found for the specified parameters'
            }), 404
        
        # Convert to DataFrame for easier export
        records = []
        for item in data:
            record = {
                'id': item.id,
                'region_id': item.region_id,
                'region_name': item.region.name if item.region else None,
                'date': item.date.isoformat(),
                'forest_area': item.forest_area,
                'deforested_area': item.deforested_area,
                'percentage_change': item.percentage_change,
                'severity': item.severity
            }
            
            # Add coordinates if available
            if item.coordinates:
                try:
                    coords = json.loads(item.coordinates)
                    if coords and 'coordinates' in coords:
                        record['longitude'] = coords['coordinates'][0]
                        record['latitude'] = coords['coordinates'][1]
                except:
                    pass
            
            records.append(record)
        
        df = pd.DataFrame(records)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"deforestation_data_{timestamp}.{format_type}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Export based on format
        if format_type == 'csv':
            df.to_csv(filepath, index=False)
            mimetype = 'text/csv'
        elif format_type == 'excel':
            df.to_excel(filepath, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif format_type == 'json':
            df.to_json(filepath, orient='records')
            mimetype = 'application/json'
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported format'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'download_url': f"/api/download-file/{filename}",
                'format': format_type,
                'records': len(df)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/download-file/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file"""
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Determine mimetype based on file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.csv':
            mimetype = 'text/csv'
        elif ext == '.xlsx':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ext == '.json':
            mimetype = 'application/json'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500