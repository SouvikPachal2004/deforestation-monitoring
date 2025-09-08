import os
import cv2
import numpy as np
import json
from datetime import datetime
import rasterio
from rasterio.plot import show
import geopandas as gpd
from shapely.geometry import shape, Point
import pandas as pd

class SatelliteImageProcessor:
    """Class for processing satellite images for deforestation analysis"""
    
    def __init__(self):
        """Initialize the satellite image processor"""
        self.supported_formats = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.jp2']
    
    def analyze_image(self, image_path):
        """
        Analyze a satellite image for deforestation
        
        Args:
            image_path (str): Path to the satellite image
            
        Returns:
            dict: Analysis results
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Get file extension
            file_ext = os.path.splitext(image_path)[1].lower()
            
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Load the image
            if file_ext in ['.tif', '.tiff', '.jp2']:
                # Use rasterio for geospatial formats
                with rasterio.open(image_path) as src:
                    img = src.read()
                    metadata = src.meta
                    transform = src.transform
                    crs = src.crs
                    bounds = src.bounds
                    
                    # Convert to numpy array for processing
                    if len(img.shape) == 3:
                        img = np.transpose(img, (1, 2, 0))
            else:
                # Use OpenCV for standard image formats
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError(f"Could not read image: {image_path}")
                
                # Convert from BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Placeholder for geospatial data
                metadata = {}
                transform = None
                crs = None
                bounds = None
            
            # Get image dimensions
            height, width = img.shape[:2]
            total_pixels = height * width
            
            # Analyze the image
            analysis_results = self._process_image(img)
            
            # Calculate statistics
            forest_area = analysis_results.get('forest_area', 0)
            deforested_area = analysis_results.get('deforested_area', 0)
            
            # Calculate percentages
            forest_percentage = (forest_area / total_pixels) * 100 if total_pixels > 0 else 0
            deforested_percentage = (deforested_area / total_pixels) * 100 if total_pixels > 0 else 0
            
            # Calculate percentage change (would need historical data for real implementation)
            percentage_change = -deforested_percentage  # Simplified for demonstration
            
            # Determine severity
            if deforested_percentage > 20:
                severity = "high"
            elif deforested_percentage > 10:
                severity = "medium"
            else:
                severity = "low"
            
            # Generate coordinates (center of the image if geospatial data is available)
            coordinates = None
            if bounds:
                coordinates = {
                    "type": "Point",
                    "coordinates": [
                        (bounds.left + bounds.right) / 2,
                        (bounds.bottom + bounds.top) / 2
                    ]
                }
            else:
                # Placeholder coordinates (center of India)
                coordinates = {
                    "type": "Point",
                    "coordinates": [78.9629, 20.5937]
                }
            
            # Create visualization
            visualization_path = self._create_visualization(image_path, analysis_results)
            
            # Return results
            return {
                'image_path': image_path,
                'visualization_path': visualization_path,
                'width': width,
                'height': height,
                'total_pixels': total_pixels,
                'forest_area': forest_area,
                'forest_percentage': forest_percentage,
                'deforested_area': deforested_area,
                'deforested_percentage': deforested_percentage,
                'percentage_change': percentage_change,
                'severity': severity,
                'coordinates': coordinates,
                'metadata': metadata,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
            return {
                'image_path': image_path,
                'error': str(e)
            }
    
    def _process_image(self, img):
        """
        Process the image to extract deforestation information
        
        Args:
            img (numpy.ndarray): The image array
            
        Returns:
            dict: Processing results
        """
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            
            # Define thresholds for forest and deforested areas
            # These would be calibrated for specific regions and satellite types
            forest_lower = np.array([25, 40, 20])
            forest_upper = np.array([90, 255, 200])
            
            deforested_lower = np.array([0, 0, 100])
            deforested_upper = np.array([180, 255, 255])
            
            # Create masks
            forest_mask = cv2.inRange(hsv, forest_lower, forest_upper)
            deforested_mask = cv2.inRange(hsv, deforested_lower, deforested_upper)
            
            # Apply morphological operations to clean up masks
            kernel = np.ones((5, 5), np.uint8)
            forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_OPEN, kernel)
            forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_CLOSE, kernel)
            
            deforested_mask = cv2.morphologyEx(deforested_mask, cv2.MORPH_OPEN, kernel)
            deforested_mask = cv2.morphologyEx(deforested_mask, cv2.MORPH_CLOSE, kernel)
            
            # Ensure deforested areas are not within forest areas
            deforested_mask = deforested_mask & ~forest_mask
            
            # Count pixels
            forest_area = np.count_nonzero(forest_mask)
            deforested_area = np.count_nonzero(deforested_mask)
            
            # Calculate NDVI (Normalized Difference Vegetation Index) if image has enough bands
            ndvi = None
            if img.shape[2] >= 3:
                # Assuming RGB image, use red and green bands as proxy for NIR and Red
                # In a real implementation, you would use actual NIR and Red bands
                red = img[:, :, 0].astype(float)
                green = img[:, :, 1].astype(float)
                
                # Avoid division by zero
                denominator = (red + green)
                denominator[denominator == 0] = 0.001
                
                ndvi = (green - red) / denominator
                
                # Threshold NDVI for vegetation
                vegetation_mask = ndvi > 0.3
                vegetation_area = np.count_nonzero(vegetation_mask)
                
                # Update forest area based on NDVI
                forest_area = max(forest_area, vegetation_area)
            
            return {
                'forest_area': forest_area,
                'deforested_area': deforested_area,
                'forest_mask': forest_mask,
                'deforested_mask': deforested_mask,
                'ndvi': ndvi
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return {
                'error': str(e)
            }
    
    def _create_visualization(self, image_path, analysis_results):
        """
        Create a visualization of the analysis results
        
        Args:
            image_path (str): Path to the original image
            analysis_results (dict): Results of the analysis
            
        Returns:
            str: Path to the visualization image
        """
        try:
            # Load the original image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Get masks
            forest_mask = analysis_results.get('forest_mask')
            deforested_mask = analysis_results.get('deforested_mask')
            
            # Create visualization
            vis = img.copy()
            
            # Overlay forest areas in green
            if forest_mask is not None:
                forest_overlay = np.zeros_like(vis)
                forest_overlay[forest_mask > 0] = [0, 255, 0]  # Green
                vis = cv2.addWeighted(vis, 1, forest_overlay, 0.5, 0)
            
            # Overlay deforested areas in red
            if deforested_mask is not None:
                deforested_overlay = np.zeros_like(vis)
                deforested_overlay[deforested_overlay > 0] = [0, 0, 255]  # Red
                vis = cv2.addWeighted(vis, 1, deforested_overlay, 0.7, 0)
            
            # Add statistics text
            forest_area = analysis_results.get('forest_area', 0)
            deforested_area = analysis_results.get('deforested_area', 0)
            total_pixels = img.shape[0] * img.shape[1]
            
            forest_percentage = (forest_area / total_pixels) * 100 if total_pixels > 0 else 0
            deforested_percentage = (deforested_area / total_pixels) * 100 if total_pixels > 0 else 0
            
            text = f"Forest: {forest_percentage:.1f}%, Deforested: {deforested_percentage:.1f}%"
            cv2.putText(vis, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Save visualization
            base_name, ext = os.path.splitext(image_path)
            visualization_path = f"{base_name}_visualization{ext}"
            cv2.imwrite(visualization_path, vis)
            
            return visualization_path
            
        except Exception as e:
            print(f"Error creating visualization: {e}")
            return None
    
    def compare_images(self, image_path1, image_path2):
        """
        Compare two satellite images to detect changes
        
        Args:
            image_path1 (str): Path to the first image (before)
            image_path2 (str): Path to the second image (after)
            
        Returns:
            dict: Comparison results
        """
        try:
            # Analyze both images
            result1 = self.analyze_image(image_path1)
            result2 = self.analyze_image(image_path2)
            
            if 'error' in result1:
                return {'error': f"Error analyzing first image: {result1['error']}"}
            
            if 'error' in result2:
                return {'error': f"Error analyzing second image: {result2['error']}"}
            
            # Calculate changes
            forest_change = result2['forest_percentage'] - result1['forest_percentage']
            deforestation_change = result2['deforested_percentage'] - result1['deforested_percentage']
            
            # Determine overall change
            if forest_change < -5:
                change_severity = "high"
            elif forest_change < -2:
                change_severity = "medium"
            else:
                change_severity = "low"
            
            # Create change visualization
            change_vis_path = self._create_change_visualization(
                image_path1, image_path2, 
                result1.get('forest_mask'), 
                result2.get('forest_mask')
            )
            
            return {
                'image1': result1,
                'image2': result2,
                'forest_change': forest_change,
                'deforestation_change': deforestation_change,
                'change_severity': change_severity,
                'change_visualization': change_vis_path
            }
            
        except Exception as e:
            print(f"Error comparing images: {e}")
            return {'error': str(e)}
    
    def _create_change_visualization(self, image_path1, image_path2, mask1, mask2):
        """
        Create a visualization showing changes between two images
        
        Args:
            image_path1 (str): Path to the first image
            image_path2 (str): Path to the second image
            mask1 (numpy.ndarray): Forest mask for the first image
            mask2 (numpy.ndarray): Forest mask for the second image
            
        Returns:
            str: Path to the change visualization image
        """
        try:
            # Load images
            img1 = cv2.imread(image_path1)
            img2 = cv2.imread(image_path2)
            
            if img1 is None or img2 is None:
                raise ValueError("Could not read one or both images")
            
            # Resize images to the same dimensions if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Create side-by-side comparison
            h, w = img1.shape[:2]
            comparison = np.zeros((h, w * 2, 3), dtype=np.uint8)
            comparison[:, :w] = img1
            comparison[:, w:] = img2
            
            # Add labels
            cv2.putText(comparison, "Before", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(comparison, "After", (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Create change map
            if mask1 is not None and mask2 is not None:
                # Ensure masks are the same size
                if mask1.shape != mask2.shape:
                    mask2 = cv2.resize(mask2, (mask1.shape[1], mask1.shape[0]))
                
                # Calculate changes
                forest_loss = mask1 & ~mask2  # Forest in first image but not in second
                forest_gain = ~mask1 & mask2  # Not forest in first image but forest in second
                
                # Create change visualization
                change_map = np.zeros_like(img1)
                change_map[forest_loss > 0] = [0, 0, 255]  # Red for forest loss
                change_map[forest_gain > 0] = [0, 255, 0]  # Green for forest gain
                
                # Blend with original image
                change_vis = cv2.addWeighted(img2, 0.7, change_map, 0.3, 0)
                
                # Add change statistics
                total_pixels = mask1.size
                forest_loss_pixels = np.count_nonzero(forest_loss)
                forest_gain_pixels = np.count_nonzero(forest_gain)
                
                forest_loss_percentage = (forest_loss_pixels / total_pixels) * 100
                forest_gain_percentage = (forest_gain_pixels / total_pixels) * 100
                
                text = f"Loss: {forest_loss_percentage:.1f}%, Gain: {forest_gain_percentage:.1f}%"
                cv2.putText(change_vis, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Save change visualization
                base_name1, ext1 = os.path.splitext(image_path1)
                change_vis_path = f"{base_name1}_change_visualization{ext1}"
                cv2.imwrite(change_vis_path, change_vis)
                
                # Create combined visualization
                combined = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)
                combined[:h, :w] = img1
                combined[:h, w:] = img2
                combined[h:, :w] = comparison[:, :w]  # Before image again
                combined[h:, w:] = change_vis
                
                # Add title
                cv2.putText(combined, "Deforestation Change Analysis", (w // 2 - 150, h - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Save combined visualization
                combined_vis_path = f"{base_name1}_combined_visualization{ext1}"
                cv2.imwrite(combined_vis_path, combined)
                
                return combined_vis_path
            
            return comparison
            
        except Exception as e:
            print(f"Error creating change visualization: {e}")
            return None
    
    def process_time_series(self, image_paths):
        """
        Process a time series of satellite images
        
        Args:
            image_paths (list): List of paths to satellite images in chronological order
            
        Returns:
            dict: Time series analysis results
        """
        try:
            if len(image_paths) < 2:
                return {'error': 'At least two images are required for time series analysis'}
            
            # Analyze each image
            results = []
            for image_path in image_paths:
                result = self.analyze_image(image_path)
                results.append(result)
            
            # Extract time series data
            dates = []
            forest_percentages = []
            deforested_percentages = []
            
            for result in results:
                if 'error' not in result:
                    # Extract date from filename or metadata
                    # In a real implementation, you would get this from metadata
                    filename = os.path.basename(result['image_path'])
                    date_str = filename.split('_')[0] if '_' in filename else '2023-01-01'
                    
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').isoformat()
                    except:
                        date = datetime.now().isoformat()
                    
                    dates.append(date)
                    forest_percentages.append(result['forest_percentage'])
                    deforested_percentages.append(result['deforested_percentage'])
            
            # Calculate trends
            forest_trend = self._calculate_trend(forest_percentages)
            deforestation_trend = self._calculate_trend(deforested_percentages)
            
            # Determine overall trend
            if forest_trend < -0.5:
                overall_trend = "decreasing"
            elif forest_trend > 0.5:
                overall_trend = "increasing"
            else:
                overall_trend = "stable"
            
            return {
                'time_series': {
                    'dates': dates,
                    'forest_percentages': forest_percentages,
                    'deforested_percentages': deforested_percentages
                },
                'trends': {
                    'forest': forest_trend,
                    'deforestation': deforestation_trend,
                    'overall': overall_trend
                },
                'individual_results': results
            }
            
        except Exception as e:
            print(f"Error processing time series: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, values):
        """
        Calculate the trend of a time series using linear regression
        
        Args:
            values (list): List of values
            
        Returns:
            float: Trend value (positive for increasing, negative for decreasing)
        """
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate linear regression
        slope, _ = np.polyfit(x, y, 1)
        
        return slope
    
    def export_to_geojson(self, analysis_results, output_path):
        """
        Export analysis results to GeoJSON format
        
        Args:
            analysis_results (dict): Results of the analysis
            output_path (str): Path to save the GeoJSON file
            
        Returns:
            str: Path to the saved GeoJSON file
        """
        try:
            features = []
            
            # Add forest area as a feature
            if 'forest_mask' in analysis_results:
                # Convert mask to polygons (simplified for demonstration)
                forest_mask = analysis_results['forest_mask']
                contours, _ = cv2.findContours(forest_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    if cv2.contourArea(contour) > 100:  # Filter small contours
                        # Simplify contour
                        epsilon = 0.01 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        # Convert to GeoJSON polygon
                        coordinates = []
                        for point in approx:
                            coordinates.append([float(point[0][0]), float(point[0][1])])
                        
                        # Close the polygon
                        if len(coordinates) > 2:
                            coordinates.append(coordinates[0])
                            
                            feature = {
                                "type": "Feature",
                                "properties": {
                                    "type": "forest",
                                    "area": cv2.contourArea(contour)
                                },
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [coordinates]
                                }
                            }
                            features.append(feature)
            
            # Add deforested area as a feature
            if 'deforested_mask' in analysis_results:
                # Convert mask to polygons (simplified for demonstration)
                deforested_mask = analysis_results['deforested_mask']
                contours, _ = cv2.findContours(deforested_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    if cv2.contourArea(contour) > 100:  # Filter small contours
                        # Simplify contour
                        epsilon = 0.01 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        # Convert to GeoJSON polygon
                        coordinates = []
                        for point in approx:
                            coordinates.append([float(point[0][0]), float(point[0][1])])
                        
                        # Close the polygon
                        if len(coordinates) > 2:
                            coordinates.append(coordinates[0])
                            
                            feature = {
                                "type": "Feature",
                                "properties": {
                                    "type": "deforested",
                                    "area": cv2.contourArea(contour)
                                },
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [coordinates]
                                }
                            }
                            features.append(feature)
            
            # Create GeoJSON
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(geojson, f)
            
            return output_path
            
        except Exception as e:
            print(f"Error exporting to GeoJSON: {e}")
            return None