import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from database.models import DeforestationData, Region

class DataAnalyzer:
    """Class for analyzing deforestation data"""
    
    def __init__(self):
        """Initialize the data analyzer"""
        pass
    
    def generate_summary_report(self, data):
        """
        Generate a summary report from deforestation data
        
        Args:
            data (list): List of DeforestationData objects
            
        Returns:
            dict: Summary report data
        """
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Calculate basic statistics
            total_area = sum(item.forest_area + item.deforested_area for item in data)
            total_forest_area = sum(item.forest_area for item in data)
            total_deforested_area = sum(item.deforested_area for item in data)
            
            # Calculate percentages
            forest_percentage = (total_forest_area / total_area) * 100 if total_area > 0 else 0
            deforested_percentage = (total_deforested_area / total_area) * 100 if total_area > 0 else 0
            
            # Calculate average percentage change
            avg_percentage_change = sum(item.percentage_change for item in data) / len(data) if data else 0
            
            # Determine overall severity
            severity_counts = {'high': 0, 'medium': 0, 'low': 0}
            for item in data:
                severity_counts[item.severity] += 1
            
            # Determine overall severity based on the majority
            if severity_counts['high'] > severity_counts['medium'] and severity_counts['high'] > severity_counts['low']:
                overall_severity = 'high'
            elif severity_counts['medium'] > severity_counts['low']:
                overall_severity = 'medium'
            else:
                overall_severity = 'low'
            
            # Get date range
            dates = [item.date for item in data]
            min_date = min(dates).isoformat()
            max_date = max(dates).isoformat()
            
            # Get region information
            region_id = data[0].region_id if data else None
            region_name = None
            if region_id:
                region = Region.query.get(region_id)
                if region:
                    region_name = region.name
            
            # Calculate monthly deforestation rates
            monthly_data = self._calculate_monthly_rates(data)
            
            # Calculate year-over-year change if we have enough data
            yoy_change = None
            if len(dates) >= 365:  # At least one year of data
                # Split data into two periods
                mid_date = min_date + (max_date - min_date) / 2
                first_period = [item for item in data if item.date < mid_date]
                second_period = [item for item in data if item.date >= mid_date]
                
                if first_period and second_period:
                    first_forest = sum(item.forest_area for item in first_period) / len(first_period)
                    second_forest = sum(item.forest_area for item in second_period) / len(second_period)
                    yoy_change = ((second_forest - first_forest) / first_forest) * 100
            
            return {
                'report_type': 'summary',
                'region_id': region_id,
                'region_name': region_name,
                'date_range': {
                    'start': min_date,
                    'end': max_date
                },
                'statistics': {
                    'total_area': total_area,
                    'total_forest_area': total_forest_area,
                    'total_deforested_area': total_deforested_area,
                    'forest_percentage': forest_percentage,
                    'deforested_percentage': deforested_percentage,
                    'avg_percentage_change': avg_percentage_change,
                    'overall_severity': overall_severity,
                    'severity_distribution': severity_counts,
                    'year_over_year_change': yoy_change
                },
                'monthly_data': monthly_data,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_detailed_report(self, data):
        """
        Generate a detailed report from deforestation data
        
        Args:
            data (list): List of DeforestationData objects
            
        Returns:
            dict: Detailed report data
        """
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Start with the summary report
            report = self.generate_summary_report(data)
            
            if 'error' in report:
                return report
            
            # Add detailed analysis
            
            # Calculate deforestation hotspots (areas with high deforestation)
            hotspots = sorted(data, key=lambda x: x.deforested_area, reverse=True)[:10]
            
            # Calculate deforestation trends
            trends = self._calculate_trends(data)
            
            # Calculate seasonal patterns
            seasonal_patterns = self._calculate_seasonal_patterns(data)
            
            # Calculate correlation with potential factors (simplified)
            correlations = self._calculate_correlations(data)
            
            # Calculate deforestation causes (simplified)
            causes = self._estimate_deforestation_causes(data)
            
            # Add detailed sections to the report
            report['report_type'] = 'detailed'
            report['hotspots'] = [
                {
                    'id': hotspot.id,
                    'date': hotspot.date.isoformat(),
                    'forest_area': hotspot.forest_area,
                    'deforested_area': hotspot.deforested_area,
                    'percentage_change': hotspot.percentage_change,
                    'severity': hotspot.severity
                }
                for hotspot in hotspots
            ]
            report['trends'] = trends
            report['seasonal_patterns'] = seasonal_patterns
            report['correlations'] = correlations
            report['causes'] = causes
            
            return report
        except Exception as e:
            return {'error': str(e)}
    
    def generate_prediction_report(self, data):
        """
        Generate a prediction report based on historical deforestation data
        
        Args:
            data (list): List of DeforestationData objects
            
        Returns:
            dict: Prediction report data
        """
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Start with the summary report
            report = self.generate_summary_report(data)
            
            if 'error' in report:
                return report
            
            # Sort data by date
            sorted_data = sorted(data, key=lambda x: x.date)
            
            # Extract time series
            dates = [item.date for item in sorted_data]
            forest_areas = [item.forest_area for item in sorted_data]
            deforested_areas = [item.deforested_area for item in sorted_data]
            
            # Predict future values (simplified linear extrapolation)
            prediction_periods = 12  # Predict next 12 periods
            forest_predictions = self._predict_linear(forest_areas, prediction_periods)
            deforestation_predictions = self._predict_linear(deforested_areas, prediction_periods)
            
            # Generate future dates
            last_date = dates[-1]
            future_dates = []
            for i in range(1, prediction_periods + 1):
                # This is a simplified approach - in a real implementation, you would handle different time intervals
                future_date = datetime(last_date.year, last_date.month, 1)
                future_date = future_date.replace(month=(future_date.month + i - 1) % 12 + 1, 
                                               year=future_date.year + (future_date.month + i - 1) // 12)
                future_dates.append(future_date.isoformat())
            
            # Calculate prediction confidence intervals (simplified)
            forest_confidence = self._calculate_confidence_interval(forest_areas, forest_predictions)
            deforestation_confidence = self._calculate_confidence_interval(deforested_areas, deforestation_predictions)
            
            # Calculate risk assessment
            risk_assessment = self._assess_deforestation_risk(data, forest_predictions, deforestation_predictions)
            
            # Add prediction sections to the report
            report['report_type'] = 'prediction'
            report['predictions'] = {
                'dates': future_dates,
                'forest_areas': forest_predictions,
                'deforested_areas': deforestation_predictions,
                'forest_confidence': forest_confidence,
                'deforestation_confidence': deforestation_confidence
            }
            report['risk_assessment'] = risk_assessment
            report['recommendations'] = self._generate_recommendations(risk_assessment)
            
            return report
        except Exception as e:
            return {'error': str(e)}
    
    def generate_impact_report(self, data):
        """
        Generate an impact report based on deforestation data
        
        Args:
            data (list): List of DeforestationData objects
            
        Returns:
            dict: Impact report data
        """
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Start with the summary report
            report = self.generate_summary_report(data)
            
            if 'error' in report:
                return report
            
            # Calculate environmental impact
            environmental_impact = self._calculate_environmental_impact(data)
            
            # Calculate biodiversity impact (simplified)
            biodiversity_impact = self._calculate_biodiversity_impact(data)
            
            # Calculate carbon impact (simplified)
            carbon_impact = self._calculate_carbon_impact(data)
            
            # Calculate economic impact (simplified)
            economic_impact = self._calculate_economic_impact(data)
            
            # Calculate social impact (simplified)
            social_impact = self._calculate_social_impact(data)
            
            # Add impact sections to the report
            report['report_type'] = 'impact'
            report['environmental_impact'] = environmental_impact
            report['biodiversity_impact'] = biodiversity_impact
            report['carbon_impact'] = carbon_impact
            report['economic_impact'] = economic_impact
            report['social_impact'] = social_impact
            report['overall_impact_score'] = self._calculate_overall_impact_score(
                environmental_impact, biodiversity_impact, carbon_impact, economic_impact, social_impact
            )
            report['mitigation_strategies'] = self._suggest_mitigation_strategies(report)
            
            return report
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_monthly_rates(self, data):
        """Calculate monthly deforestation rates"""
        try:
            # Group data by month
            monthly_data = {}
            for item in data:
                month_key = (item.date.year, item.date.month)
                if month_key not in monthly_data:
                    monthly_data[month_key] = []
                monthly_data[month_key].append(item)
            
            # Calculate monthly averages
            monthly_rates = []
            for (year, month), items in monthly_data.items():
                avg_forest = sum(item.forest_area for item in items) / len(items)
                avg_deforested = sum(item.deforested_area for item in items) / len(items)
                avg_change = sum(item.percentage_change for item in items) / len(items)
                
                monthly_rates.append({
                    'year': year,
                    'month': month,
                    'avg_forest_area': avg_forest,
                    'avg_deforested_area': avg_deforested,
                    'avg_percentage_change': avg_change
                })
            
            # Sort by date
            monthly_rates.sort(key=lambda x: (x['year'], x['month']))
            
            return monthly_rates
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_trends(self, data):
        """Calculate deforestation trends"""
        try:
            # Sort data by date
            sorted_data = sorted(data, key=lambda x: x.date)
            
            # Extract time series
            dates = [item.date for item in sorted_data]
            forest_areas = [item.forest_area for item in sorted_data]
            deforested_areas = [item.deforested_area for item in sorted_data]
            
            # Calculate linear trends
            forest_trend = self._calculate_linear_trend(forest_areas)
            deforestation_trend = self._calculate_linear_trend(deforested_areas)
            
            # Calculate acceleration (change in trend)
            forest_acceleration = self._calculate_acceleration(forest_areas)
            deforestation_acceleration = self._calculate_acceleration(deforested_areas)
            
            return {
                'forest_trend': {
                    'slope': forest_trend['slope'],
                    'direction': 'increasing' if forest_trend['slope'] > 0 else 'decreasing',
                    'r_squared': forest_trend['r_squared']
                },
                'deforestation_trend': {
                    'slope': deforestation_trend['slope'],
                    'direction': 'increasing' if deforestation_trend['slope'] > 0 else 'decreasing',
                    'r_squared': deforestation_trend['r_squared']
                },
                'forest_acceleration': forest_acceleration,
                'deforestation_acceleration': deforestation_acceleration
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_seasonal_patterns(self, data):
        """Calculate seasonal patterns in deforestation"""
        try:
            # Group data by month
            monthly_data = {}
            for item in data:
                month = item.date.month
                if month not in monthly_data:
                    monthly_data[month] = []
                monthly_data[month].append(item.deforested_area)
            
            # Calculate monthly averages
            monthly_averages = {}
            for month, values in monthly_data.items():
                monthly_averages[month] = sum(values) / len(values)
            
            # Identify high and low deforestation months
            sorted_months = sorted(monthly_averages.items(), key=lambda x: x[1])
            low_months = [month for month, _ in sorted_months[:3]]
            high_months = [month for month, _ in sorted_months[-3:]]
            
            # Calculate seasonal index
            total_avg = sum(monthly_averages.values()) / len(monthly_averages)
            seasonal_index = {}
            for month, avg in monthly_averages.items():
                seasonal_index[month] = avg / total_avg
            
            return {
                'monthly_averages': monthly_averages,
                'low_deforestation_months': low_months,
                'high_deforestation_months': high_months,
                'seasonal_index': seasonal_index
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_correlations(self, data):
        """Calculate correlations with potential factors (simplified)"""
        try:
            # In a real implementation, you would include data on factors like
            # rainfall, temperature, population density, etc.
            # For now, we'll return placeholder data
            
            return {
                'rainfall': {
                    'correlation': -0.65,
                    'interpretation': 'Moderate negative correlation - less rainfall associated with more deforestation'
                },
                'temperature': {
                    'correlation': 0.42,
                    'interpretation': 'Weak positive correlation - higher temperatures associated with more deforestation'
                },
                'population_density': {
                    'correlation': 0.78,
                    'interpretation': 'Strong positive correlation - higher population density associated with more deforestation'
                },
                'distance_to_roads': {
                    'correlation': -0.53,
                    'interpretation': 'Moderate negative correlation - deforestation decreases with distance from roads'
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _estimate_deforestation_causes(self, data):
        """Estimate deforestation causes (simplified)"""
        try:
            # In a real implementation, you would use more sophisticated methods
            # For now, we'll return placeholder data
            
            return {
                'agricultural_expansion': {
                    'percentage': 40,
                    'description': 'Conversion of forest land to agricultural use'
                },
                'logging': {
                    'percentage': 20,
                    'description': 'Commercial and subsistence logging activities'
                },
                'infrastructure_development': {
                    'percentage': 15,
                    'description': 'Construction of roads, buildings, and other infrastructure'
                },
                'mining': {
                    'percentage': 10,
                    'description': 'Mining and extraction activities'
                },
                'urban_expansion': {
                    'percentage': 8,
                    'description': 'Expansion of urban areas and settlements'
                },
                'wildfires': {
                    'percentage': 5,
                    'description': 'Forest fires and burning activities'
                },
                'other': {
                    'percentage': 2,
                    'description': 'Other causes of deforestation'
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _predict_linear(self, values, periods):
        """Predict future values using linear extrapolation"""
        try:
            if len(values) < 2:
                return [values[-1]] * periods if values else [0] * periods
            
            x = np.arange(len(values))
            y = np.array(values)
            
            # Fit linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict future values
            predictions = []
            for i in range(1, periods + 1):
                pred = slope * (len(values) + i - 1) + intercept
                predictions.append(max(0, pred))  # Ensure non-negative
            
            return predictions
        except Exception as e:
            return [0] * periods
    
    def _calculate_confidence_interval(self, historical, predicted):
        """Calculate confidence interval for predictions (simplified)"""
        try:
            if len(historical) < 2:
                return {'lower': predicted, 'upper': predicted}
            
            # Calculate standard deviation of historical data
            std_dev = np.std(historical)
            
            # Calculate confidence interval (95% confidence)
            margin_of_error = 1.96 * std_dev
            
            return {
                'lower': [max(0, p - margin_of_error) for p in predicted],
                'upper': [p + margin_of_error for p in predicted]
            }
        except Exception as e:
            return {'lower': predicted, 'upper': predicted}
    
    def _assess_deforestation_risk(self, data, forest_predictions, deforestation_predictions):
        """Assess deforestation risk based on predictions"""
        try:
            # Calculate current forest area
            current_forest = data[-1].forest_area if data else 0
            
            # Calculate predicted forest loss
            predicted_forest_loss = current_forest - forest_predictions[-1]
            predicted_forest_loss_percentage = (predicted_forest_loss / current_forest) * 100 if current_forest > 0 else 0
            
            # Calculate predicted deforestation increase
            current_deforestation = data[-1].deforested_area if data else 0
            predicted_deforestation_increase = deforestation_predictions[-1] - current_deforestation
            predicted_deforestation_increase_percentage = (predicted_deforestation_increase / current_deforestation) * 100 if current_deforestation > 0 else 0
            
            # Determine risk level
            if predicted_forest_loss_percentage > 20 or predicted_deforestation_increase_percentage > 50:
                risk_level = 'high'
            elif predicted_forest_loss_percentage > 10 or predicted_deforestation_increase_percentage > 25:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'risk_level': risk_level,
                'predicted_forest_loss': predicted_forest_loss,
                'predicted_forest_loss_percentage': predicted_forest_loss_percentage,
                'predicted_deforestation_increase': predicted_deforestation_increase,
                'predicted_deforestation_increase_percentage': predicted_deforestation_increase_percentage,
                'timeframe': f'next {len(forest_predictions)} periods'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_recommendations(self, risk_assessment):
        """Generate recommendations based on risk assessment"""
        try:
            risk_level = risk_assessment.get('risk_level', 'low')
            recommendations = []
            
            if risk_level == 'high':
                recommendations.extend([
                    'Implement immediate conservation measures in high-risk areas',
                    'Increase monitoring frequency in critical zones',
                    'Engage local communities in forest protection efforts',
                    'Strengthen law enforcement against illegal logging'
                ])
            elif risk_level == 'medium':
                recommendations.extend([
                    'Develop targeted conservation plans for vulnerable areas',
                    'Increase community awareness about deforestation impacts',
                    'Promote sustainable land use practices',
                    'Establish early warning systems for deforestation activities'
                ])
            else:
                recommendations.extend([
                    'Maintain current conservation efforts',
                    'Continue regular monitoring of forest areas',
                    'Support reforestation and afforestation initiatives',
                    'Promote sustainable development practices'
                ])
            
            # Add general recommendations
            recommendations.extend([
                'Invest in remote sensing technology for better monitoring',
                'Develop policies that balance economic development with forest conservation',
                'Create incentives for forest conservation and sustainable management',
                'Strengthen international cooperation on forest protection'
            ])
            
            return recommendations
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_environmental_impact(self, data):
        """Calculate environmental impact of deforestation"""
        try:
            # Calculate total deforested area
            total_deforested = sum(item.deforested_area for item in data)
            
            # Estimate tree loss (simplified)
            trees_per_hectare = 500  # Average estimate
            estimated_tree_loss = total_deforested * trees_per_hectare
            
            # Estimate habitat loss (simplified)
            species_per_hectare = 50  # Average estimate
            estimated_species_impact = total_deforested * species_per_hectare
            
            # Estimate soil erosion risk (simplified)
            erosion_risk = min(100, (total_deforested / 1000) * 10)  # Simplified calculation
            
            # Estimate water cycle impact (simplified)
            water_impact = min(100, (total_deforested / 1000) * 15)  # Simplified calculation
            
            return {
                'total_deforested_area': total_deforested,
                'estimated_tree_loss': estimated_tree_loss,
                'estimated_species_impact': estimated_species_impact,
                'soil_erosion_risk': erosion_risk,
                'water_cycle_impact': water_impact
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_biodiversity_impact(self, data):
        """Calculate biodiversity impact of deforestation"""
        try:
            # Calculate total deforested area
            total_deforested = sum(item.deforested_area for item in data)
            
            # Estimate species at risk (simplified)
            species_density_per_hectare = 10  # Average estimate
            estimated_species_at_risk = total_deforested * species_density_per_hectare
            
            # Estimate habitat fragmentation (simplified)
            fragmentation_index = min(100, (total_deforested / 1000) * 20)  # Simplified calculation
            
            # Estimate ecosystem services loss (simplified)
            ecosystem_services_value_per_hectare = 5000  # USD per year
            estimated_ecosystem_services_loss = total_deforested * ecosystem_services_value_per_hectare
            
            return {
                'total_deforested_area': total_deforested,
                'estimated_species_at_risk': estimated_species_at_risk,
                'fragmentation_index': fragmentation_index,
                'estimated_ecosystem_services_loss': estimated_ecosystem_services_loss
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_carbon_impact(self, data):
        """Calculate carbon impact of deforestation"""
        try:
            # Calculate total deforested area
            total_deforested = sum(item.deforested_area for item in data)
            
            # Estimate carbon storage in forests (simplified)
            carbon_per_hectare = 200  # Tons of carbon per hectare
            estimated_carbon_loss = total_deforested * carbon_per_hectare
            
            # Convert to CO2 equivalent
            co2_conversion_factor = 3.67
            estimated_co2_equivalent = estimated_carbon_loss * co2_conversion_factor
            
            # Estimate carbon sequestration loss (simplified)
            annual_sequestration_per_hectare = 5  # Tons of carbon per hectare per year
            estimated_sequestration_loss = total_deforested * annual_sequestration_per_hectare
            
            return {
                'total_deforested_area': total_deforested,
                'estimated_carbon_loss': estimated_carbon_loss,
                'estimated_co2_equivalent': estimated_co2_equivalent,
                'estimated_sequestration_loss': estimated_sequestration_loss
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_economic_impact(self, data):
        """Calculate economic impact of deforestation"""
        try:
            # Calculate total deforested area
            total_deforested = sum(item.deforested_area for item in data)
            
            # Estimate timber value loss (simplified)
            timber_value_per_hectare = 10000  # USD
            estimated_timber_value_loss = total_deforested * timber_value_per_hectare
            
            # Estimate non-timber forest products value loss (simplified)
            ntfp_value_per_hectare = 2000  # USD per year
            estimated_ntfp_value_loss = total_deforested * ntfp_value_per_hectare
            
            # Estimate ecotourism value loss (simplified)
            ecotourism_value_per_hectare = 500  # USD per year
            estimated_ecotourism_value_loss = total_deforested * ecotourism_value_per_hectare
            
            # Estimate mitigation costs (simplified)
            mitigation_cost_per_hectare = 5000  # USD
            estimated_mitigation_costs = total_deforested * mitigation_cost_per_hectare
            
            return {
                'total_deforested_area': total_deforested,
                'estimated_timber_value_loss': estimated_timber_value_loss,
                'estimated_ntfp_value_loss': estimated_ntfp_value_loss,
                'estimated_ecotourism_value_loss': estimated_ecotourism_value_loss,
                'estimated_mitigation_costs': estimated_mitigation_costs,
                'total_economic_impact': sum([
                    estimated_timber_value_loss,
                    estimated_ntfp_value_loss,
                    estimated_ecotourism_value_loss,
                    estimated_mitigation_costs
                ])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_social_impact(self, data):
        """Calculate social impact of deforestation"""
        try:
            # Calculate total deforested area
            total_deforested = sum(item.deforested_area for item in data)
            
            # Estimate people affected (simplified)
            population_density_per_hectare = 10  # People per hectare
            estimated_people_affected = total_deforested * population_density_per_hectare
            
            # Estimate indigenous communities affected (simplified)
            indigenous_percentage = 20  # Percentage of affected people who are indigenous
            estimated_indigenous_affected = estimated_people_affected * (indigenous_percentage / 100)
            
            # Estimate cultural impact (simplified)
            cultural_sites_per_hectare = 0.1  # Cultural sites per hectare
            estimated_cultural_sites_impacted = total_deforested * cultural_sites_per_hectare
            
            # Estimate livelihood impact (simplified)
            livelihood_dependency_percentage = 30  # Percentage of population dependent on forests
            estimated_livelihoods_affected = estimated_people_affected * (livelihood_dependency_percentage / 100)
            
            return {
                'total_deforested_area': total_deforested,
                'estimated_people_affected': estimated_people_affected,
                'estimated_indigenous_affected': estimated_indigenous_affected,
                'estimated_cultural_sites_impacted': estimated_cultural_sites_impacted,
                'estimated_livelihoods_affected': estimated_livelihoods_affected
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_overall_impact_score(self, environmental, biodiversity, carbon, economic, social):
        """Calculate an overall impact score"""
        try:
            # Normalize impact scores (simplified)
            env_score = min(100, environmental.get('total_deforested_area', 0) / 100)
            bio_score = min(100, biodiversity.get('estimated_species_at_risk', 0) / 10)
            carbon_score = min(100, carbon.get('estimated_co2_equivalent', 0) / 1000)
            econ_score = min(100, economic.get('total_economic_impact', 0) / 100000)
            social_score = min(100, social.get('estimated_people_affected', 0) / 100)
            
            # Calculate weighted average
            weights = {
                'environmental': 0.3,
                'biodiversity': 0.25,
                'carbon': 0.2,
                'economic': 0.15,
                'social': 0.1
            }
            
            overall_score = (
                env_score * weights['environmental'] +
                bio_score * weights['biodiversity'] +
                carbon_score * weights['carbon'] +
                econ_score * weights['economic'] +
                social_score * weights['social']
            )
            
            # Determine impact level
            if overall_score > 70:
                impact_level = 'severe'
            elif overall_score > 40:
                impact_level = 'moderate'
            else:
                impact_level = 'low'
            
            return {
                'overall_score': overall_score,
                'impact_level': impact_level,
                'component_scores': {
                    'environmental': env_score,
                    'biodiversity': bio_score,
                    'carbon': carbon_score,
                    'economic': econ_score,
                    'social': social_score
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _suggest_mitigation_strategies(self, report):
        """Suggest mitigation strategies based on impact assessment"""
        try:
            impact_level = report.get('overall_impact_score', {}).get('impact_level', 'low')
            strategies = []
            
            if impact_level == 'severe':
                strategies.extend([
                    'Implement emergency conservation measures',
                    'Establish protected areas in critical zones',
                    'Launch large-scale reforestation programs',
                    'Provide alternative livelihoods for affected communities',
                    'Strengthen law enforcement and monitoring'
                ])
            elif impact_level == 'moderate':
                strategies.extend([
                    'Develop targeted conservation plans',
                    'Promote sustainable land use practices',
                    'Support community-based forest management',
                    'Implement payment for ecosystem services programs',
                    'Enhance monitoring and early warning systems'
                ])
            else:
                strategies.extend([
                    'Maintain current conservation efforts',
                    'Support small-scale reforestation initiatives',
                    'Promote sustainable forestry practices',
                    'Raise awareness about forest conservation',
                    'Develop ecotourism opportunities'
                ])
            
            # Add general strategies
            strategies.extend([
                'Integrate forest conservation into land use planning',
                'Develop policies that address drivers of deforestation',
                'Promote sustainable agricultural practices',
                'Strengthen international cooperation on forest protection',
                'Invest in research and monitoring technologies'
            ])
            
            return strategies
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_linear_trend(self, values):
        """Calculate linear trend of a time series"""
        try:
            if len(values) < 2:
                return {'slope': 0, 'r_squared': 0}
            
            x = np.arange(len(values))
            y = np.array(values)
            
            # Fit linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared
            }
        except Exception as e:
            return {'slope': 0, 'r_squared': 0}
    
    def _calculate_acceleration(self, values):
        """Calculate acceleration (change in trend)"""
        try:
            if len(values) < 3:
                return 0
            
            # Split data into two halves
            mid_point = len(values) // 2
            first_half = values[:mid_point]
            second_half = values[mid_point:]
            
            # Calculate trends for each half
            first_trend = self._calculate_linear_trend(first_half)['slope']
            second_trend = self._calculate_linear_trend(second_half)['slope']
            
            # Calculate acceleration
            acceleration = second_trend - first_trend
            
            return acceleration
        except Exception as e:
            return 0