import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math

class TimeSeriesAnalyzer:
    """Class for analyzing time series data related to deforestation"""
    
    def __init__(self):
        """Initialize the time series analyzer"""
        pass
    
    def analyze_trend(self, data):
        """
        Analyze trend in time series data
        
        Args:
            data (list): List of values
            
        Returns:
            dict: Trend analysis results
        """
        try:
            if not data or len(data) < 2:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Calculate linear trend
            x = np.arange(len(ts))
            y = ts.values
            
            # Fit linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Determine trend direction
            if abs(slope) < 0.01:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            # Calculate percentage change
            if len(data) >= 2:
                percentage_change = ((data[-1] - data[0]) / data[0]) * 100
            else:
                percentage_change = 0
            
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'direction': direction,
                'percentage_change': percentage_change,
                'start_value': data[0],
                'end_value': data[-1],
                'data_points': len(data)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def detect_seasonality(self, data, period=None):
        """
        Detect seasonality in time series data
        
        Args:
            data (list): List of values
            period (int, optional): Seasonal period. If None, will be auto-detected
            
        Returns:
            dict: Seasonality analysis results
        """
        try:
            if not data or len(data) < 24:  # Need at least 2 periods for monthly data
                return {'error': 'Insufficient data for seasonality analysis'}
            
            # Convert to pandas Series with datetime index
            ts = pd.Series(data)
            
            # Auto-detect period if not provided
            if period is None:
                # Try common periods (12 for monthly, 4 for quarterly)
                periods_to_try = [12, 4]
                best_period = 12  # Default to monthly
                best_score = float('inf')
                
                for p in periods_to_try:
                    if len(ts) >= 2 * p:
                        try:
                            # Calculate seasonal strength
                            decomposition = seasonal_decompose(ts, model='additive', period=p)
                            seasonal = decomposition.seasonal
                            residual = decomposition.resid.dropna()
                            
                            if len(residual) > 0:
                                # Calculate variance ratio
                                seasonal_var = np.var(seasonal)
                                residual_var = np.var(residual)
                                
                                if residual_var > 0:
                                    score = residual_var / seasonal_var
                                    if score < best_score:
                                        best_score = score
                                        best_period = p
                        except:
                            continue
                
                period = best_period
            
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(ts, model='additive', period=period)
            
            # Extract components
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal
            residual = decomposition.resid.dropna()
            
            # Calculate seasonal strength
            if len(residual) > 0:
                seasonal_var = np.var(seasonal)
                residual_var = np.var(residual)
                
                if residual_var > 0:
                    seasonal_strength = seasonal_var / (seasonal_var + residual_var)
                else:
                    seasonal_strength = 0
            else:
                seasonal_strength = 0
            
            # Determine if seasonality is significant
            significant_seasonality = seasonal_strength > 0.6
            
            # Extract seasonal pattern
            seasonal_pattern = {}
            for i in range(period):
                if i < len(seasonal):
                    seasonal_pattern[i] = seasonal[i]
            
            return {
                'period': period,
                'seasonal_strength': seasonal_strength,
                'significant_seasonality': significant_seasonality,
                'seasonal_pattern': seasonal_pattern,
                'trend': trend.tolist(),
                'seasonal': seasonal.tolist(),
                'residual': residual.tolist()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def detect_anomalies(self, data, threshold=2.0):
        """
        Detect anomalies in time series data
        
        Args:
            data (list): List of values
            threshold (float): Threshold for anomaly detection (in standard deviations)
            
        Returns:
            dict: Anomaly detection results
        """
        try:
            if not data or len(data) < 3:
                return {'error': 'Insufficient data for anomaly detection'}
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Calculate rolling statistics
            window = min(12, len(ts) // 3)  # Use a reasonable window size
            rolling_mean = ts.rolling(window=window).mean()
            rolling_std = ts.rolling(window=window).std()
            
            # Calculate z-scores
            z_scores = (ts - rolling_mean) / rolling_std
            
            # Identify anomalies
            anomalies = []
            anomaly_indices = []
            
            for i, z_score in enumerate(z_scores):
                if not math.isnan(z_score) and abs(z_score) > threshold:
                    anomalies.append({
                        'index': i,
                        'value': data[i],
                        'z_score': z_score,
                        'type': 'high' if z_score > 0 else 'low'
                    })
                    anomaly_indices.append(i)
            
            # Calculate anomaly rate
            anomaly_rate = len(anomalies) / len(data)
            
            return {
                'anomalies': anomalies,
                'anomaly_indices': anomaly_indices,
                'anomaly_rate': anomaly_rate,
                'threshold': threshold,
                'z_scores': z_scores.fillna(0).tolist()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def predict(self, data, periods, method='ets'):
        """
        Predict future values of time series data
        
        Args:
            data (list): List of historical values
            periods (int): Number of periods to predict
            method (str): Prediction method ('ets', 'arima', 'linear')
            
        Returns:
            list: Predicted values
        """
        try:
            if not data or len(data) < 3:
                return [0] * periods
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            if method == 'ets':
                return self._predict_ets(ts, periods)
            elif method == 'arima':
                return self._predict_arima(ts, periods)
            elif method == 'linear':
                return self._predict_linear(ts, periods)
            else:
                return self._predict_ets(ts, periods)  # Default to ETS
        except Exception as e:
            print(f"Error in prediction: {e}")
            return [0] * periods
    
    def _predict_ets(self, ts, periods):
        """Predict using Exponential Smoothing (ETS)"""
        try:
            # Try different ETS models
            models = [
                ('add', 'add'),  # Additive trend, additive seasonality
                ('add', 'mul'),  # Additive trend, multiplicative seasonality
                ('mul', 'add'),  # Multiplicative trend, additive seasonality
                ('mul', 'mul')   # Multiplicative trend, multiplicative seasonality
            ]
            
            best_model = None
            best_aic = float('inf')
            best_predictions = None
            
            for trend, seasonal in models:
                try:
                    # Determine seasonal period
                    period = min(12, len(ts) // 2)
                    
                    # Fit ETS model
                    model = ExponentialSmoothing(
                        ts,
                        trend=trend,
                        seasonal=seasonal,
                        seasonal_periods=period
                    )
                    
                    fit = model.fit()
                    
                    # Check if this model is better
                    if hasattr(fit, 'aic') and fit.aic < best_aic:
                        best_aic = fit.aic
                        best_model = fit
                except Exception as e:
                    continue
            
            # If no model was fitted, use a simple model
            if best_model is None:
                model = ExponentialSmoothing(ts, trend='add')
                best_model = model.fit()
            
            # Make predictions
            predictions = best_model.forecast(periods)
            
            # Ensure predictions are non-negative
            predictions = [max(0, pred) for pred in predictions]
            
            return predictions
        except Exception as e:
            print(f"Error in ETS prediction: {e}")
            return self._predict_linear(ts, periods)
    
    def _predict_arima(self, ts, periods):
        """Predict using ARIMA model"""
        try:
            # Try different ARIMA parameters
            params = [
                (1, 1, 1),
                (1, 1, 0),
                (0, 1, 1),
                (2, 1, 1),
                (1, 1, 2)
            ]
            
            best_model = None
            best_aic = float('inf')
            best_predictions = None
            
            for p, d, q in params:
                try:
                    # Fit ARIMA model
                    model = ARIMA(ts, order=(p, d, q))
                    fit = model.fit()
                    
                    # Check if this model is better
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_model = fit
                except Exception as e:
                    continue
            
            # If no model was fitted, use a simple model
            if best_model is None:
                model = ARIMA(ts, order=(1, 1, 1))
                best_model = model.fit()
            
            # Make predictions
            predictions = best_model.forecast(periods)
            
            # Ensure predictions are non-negative
            predictions = [max(0, pred) for pred in predictions]
            
            return predictions
        except Exception as e:
            print(f"Error in ARIMA prediction: {e}")
            return self._predict_linear(ts, periods)
    
    def _predict_linear(self, ts, periods):
        """Predict using linear extrapolation"""
        try:
            if len(ts) < 2:
                return [0] * periods
            
            x = np.arange(len(ts))
            y = ts.values
            
            # Fit linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict future values
            predictions = []
            for i in range(1, periods + 1):
                pred = slope * (len(ts) + i - 1) + intercept
                predictions.append(max(0, pred))  # Ensure non-negative
            
            return predictions
        except Exception as e:
            print(f"Error in linear prediction: {e}")
            return [ts.iloc[-1]] * periods if len(ts) > 0 else [0] * periods
    
    def forecast_with_intervals(self, data, periods, alpha=0.05, method='ets'):
        """
        Forecast future values with confidence intervals
        
        Args:
            data (list): List of historical values
            periods (int): Number of periods to forecast
            alpha (float): Significance level for confidence intervals
            method (str): Forecasting method
            
        Returns:
            dict: Forecast results with confidence intervals
        """
        try:
            if not data or len(data) < 3:
                return {
                    'forecast': [0] * periods,
                    'lower_bound': [0] * periods,
                    'upper_bound': [0] * periods
                }
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Get point forecast
            forecast = self.predict(data, periods, method)
            
            # Calculate prediction intervals (simplified)
            residuals = ts.diff().dropna()
            if len(residuals) > 0:
                residual_std = np.std(residuals)
                
                # Calculate standard error of forecast
                se = residual_std * np.sqrt(np.arange(1, periods + 1))
                
                # Calculate confidence intervals
                z_score = 1.96  # For 95% confidence interval
                lower_bound = [max(0, f - z_score * s) for f, s in zip(forecast, se)]
                upper_bound = [f + z_score * s for f, s in zip(forecast, se)]
            else:
                lower_bound = [max(0, f * 0.8) for f in forecast]
                upper_bound = [f * 1.2 for f in forecast]
            
            return {
                'forecast': forecast,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'confidence_level': (1 - alpha) * 100
            }
        except Exception as e:
            print(f"Error in forecast with intervals: {e}")
            return {
                'forecast': self.predict(data, periods, method),
                'lower_bound': [0] * periods,
                'upper_bound': [0] * periods
            }
    
    def calculate_trend(self, values):
        """
        Calculate the trend of a time series using linear regression
        
        Args:
            values (list): List of values
            
        Returns:
            float: Trend value (positive for increasing, negative for decreasing)
        """
        try:
            if len(values) < 2:
                return 0
            
            x = np.arange(len(values))
            y = np.array(values)
            
            # Calculate linear regression
            slope, _ = np.polyfit(x, y, 1)
            
            return slope
        except Exception as e:
            print(f"Error calculating trend: {e}")
            return 0
    
    def detect_change_points(self, data, threshold=1.0):
        """
        Detect change points in time series data
        
        Args:
            data (list): List of values
            threshold (float): Threshold for change point detection
            
        Returns:
            dict: Change point detection results
        """
        try:
            if not data or len(data) < 5:
                return {'error': 'Insufficient data for change point detection'}
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Calculate cumulative sum
            mean = np.mean(ts)
            deviation = ts - mean
            cumulative_sum = np.cumsum(deviation)
            
            # Find points where cumulative sum exceeds threshold
            change_points = []
            for i in range(1, len(cumulative_sum)):
                if abs(cumulative_sum[i]) > threshold * np.std(deviation):
                    change_points.append({
                        'index': i,
                        'value': data[i],
                        'cumulative_sum': cumulative_sum[i]
                    })
            
            # Group nearby change points
            grouped_change_points = []
            if change_points:
                current_group = [change_points[0]]
                
                for cp in change_points[1:]:
                    if cp['index'] - current_group[-1]['index'] < 5:  # Group points within 5 indices
                        current_group.append(cp)
                    else:
                        # Find the point with maximum absolute cumulative sum in the group
                        max_cp = max(current_group, key=lambda x: abs(x['cumulative_sum']))
                        grouped_change_points.append(max_cp)
                        current_group = [cp]
                
                # Add the last group
                if current_group:
                    max_cp = max(current_group, key=lambda x: abs(x['cumulative_sum']))
                    grouped_change_points.append(max_cp)
            
            return {
                'change_points': grouped_change_points,
                'cumulative_sum': cumulative_sum.tolist(),
                'threshold': threshold
            }
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_moving_average(self, data, window=3):
        """
        Calculate moving average of time series data
        
        Args:
            data (list): List of values
            window (int): Window size for moving average
            
        Returns:
            list: Moving average values
        """
        try:
            if not data:
                return []
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Calculate moving average
            moving_avg = ts.rolling(window=window).mean()
            
            # Fill NaN values with original values
            moving_avg = moving_avg.fillna(ts)
            
            return moving_avg.tolist()
        except Exception as e:
            print(f"Error calculating moving average: {e}")
            return data
    
    def calculate_growth_rate(self, data):
        """
        Calculate growth rate of time series data
        
        Args:
            data (list): List of values
            
        Returns:
            list: Growth rate values
        """
        try:
            if not data or len(data) < 2:
                return []
            
            growth_rates = []
            for i in range(1, len(data)):
                if data[i-1] != 0:
                    growth_rate = ((data[i] - data[i-1]) / data[i-1]) * 100
                else:
                    growth_rate = 0
                growth_rates.append(growth_rate)
            
            return growth_rates
        except Exception as e:
            print(f"Error calculating growth rate: {e}")
            return []
    
    def decompose_time_series(self, data, period=None, model='additive'):
        """
        Decompose time series into trend, seasonal, and residual components
        
        Args:
            data (list): List of values
            period (int, optional): Seasonal period
            model (str): 'additive' or 'multiplicative'
            
        Returns:
            dict: Decomposed components
        """
        try:
            if not data or len(data) < 24:  # Need at least 2 periods for monthly data
                return {'error': 'Insufficient data for time series decomposition'}
            
            # Convert to pandas Series
            ts = pd.Series(data)
            
            # Auto-detect period if not provided
            if period is None:
                period = 12  # Default to monthly
            
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(ts, model=model, period=period)
            
            # Extract components
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal
            residual = decomposition.resid.dropna()
            
            return {
                'trend': trend.tolist(),
                'seasonal': seasonal.tolist(),
                'residual': residual.tolist(),
                'period': period,
                'model': model
            }
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_forecast(self, actual, predicted):
        """
        Evaluate forecast accuracy
        
        Args:
            actual (list): Actual values
            predicted (list): Predicted values
            
        Returns:
            dict: Forecast evaluation metrics
        """
        try:
            if not actual or not predicted or len(actual) != len(predicted):
                return {'error': 'Invalid input for forecast evaluation'}
            
            # Convert to numpy arrays
            actual_array = np.array(actual)
            predicted_array = np.array(predicted)
            
            # Calculate metrics
            mse = mean_squared_error(actual_array, predicted_array)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(actual_array, predicted_array)
            
            # Calculate Mean Absolute Percentage Error (MAPE)
            mape = np.mean(np.abs((actual_array - predicted_array) / actual_array)) * 100
            
            # Calculate R-squared
            ss_res = np.sum((actual_array - predicted_array) ** 2)
            ss_tot = np.sum((actual_array - np.mean(actual_array)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'r_squared': r_squared
            }
        except Exception as e:
            return {'error': str(e)}