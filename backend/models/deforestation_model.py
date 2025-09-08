import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import json
from datetime import datetime

class DeforestationModel:
    """Class for detecting deforestation using machine learning models"""
    
    def __init__(self):
        """Initialize the deforestation model"""
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained deforestation detection model"""
        try:
            # In a real implementation, you would load your actual model
            # model_path = os.path.join(os.path.dirname(__file__), '../models/deforestation_model.h5')
            # self.model = load_model(model_path)
            
            # For demonstration, we'll just create a placeholder
            self.model = "Deforestation Detection Model"
            print("Deforestation model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def detect_deforestation(self, image_paths):
        """
        Detect deforestation in satellite images
        
        Args:
            image_paths (list): List of paths to satellite images
            
        Returns:
            dict: Results of deforestation detection
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        results = {
            "images": [],
            "summary": {
                "total_area": 0,
                "forested_area": 0,
                "deforested_area": 0,
                "percentage_change": 0,
                "severity": "low"
            }
        }
        
        total_forest_area = 0
        total_deforested_area = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load and preprocess the image
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError(f"Could not load image: {image_path}")
                
                height, width = img.shape[:2]
                total_pixels = height * width
                
                # In a real implementation, you would use the model to make predictions
                # For demonstration, we'll simulate the results
                np.random.seed(i)  # For reproducible results
                
                # Simulate forest and deforested areas
                forest_percentage = np.random.uniform(0.4, 0.8)
                deforested_percentage = np.random.uniform(0.05, 0.3)
                
                # Ensure they don't overlap too much
                if forest_percentage + deforested_percentage > 0.9:
                    deforested_percentage = 0.9 - forest_percentage
                
                forest_area = int(forest_percentage * total_pixels)
                deforested_area = int(deforested_percentage * total_pixels)
                
                total_forest_area += forest_area
                total_deforested_area += deforested_area
                
                # Determine severity
                if deforested_percentage > 0.2:
                    severity = "high"
                elif deforested_percentage > 0.1:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Create a mock segmentation map
                segmentation_map = np.zeros((height, width), dtype=np.uint8)
                
                # Randomly place forest and deforested areas
                forest_mask = np.random.random((height, width)) < forest_percentage
                deforested_mask = np.random.random((height, width)) < deforested_percentage
                
                # Ensure deforested areas are within forest areas
                deforested_mask = deforested_mask & forest_mask
                
                segmentation_map[forest_mask] = 1  # Forest
                segmentation_map[deforested_mask] = 2  # Deforested
                
                # Save the segmentation map
                segmentation_path = image_path.replace('.', '_segmentation.')
                cv2.imwrite(segmentation_path, segmentation_map * 127)
                
                # Calculate percentage change (compared to previous image if available)
                percentage_change = 0
                if i > 0:
                    prev_forest_percentage = results["images"][i-1]["forest_percentage"]
                    percentage_change = ((forest_percentage - prev_forest_percentage) / prev_forest_percentage) * 100
                
                # Add image results
                results["images"].append({
                    "image_path": image_path,
                    "segmentation_path": segmentation_path,
                    "width": width,
                    "height": height,
                    "total_pixels": total_pixels,
                    "forest_area": forest_area,
                    "forest_percentage": forest_percentage,
                    "deforested_area": deforested_area,
                    "deforested_percentage": deforested_percentage,
                    "percentage_change": percentage_change,
                    "severity": severity
                })
                
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                results["images"].append({
                    "image_path": image_path,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        results["summary"]["total_area"] = sum(img.get("total_pixels", 0) for img in results["images"])
        results["summary"]["forested_area"] = total_forest_area
        results["summary"]["deforested_area"] = total_deforested_area
        
        if results["summary"]["total_area"] > 0:
            forest_percentage = (total_forest_area / results["summary"]["total_area"]) * 100
            deforested_percentage = (total_deforested_area / results["summary"]["total_area"]) * 100
            
            results["summary"]["forest_percentage"] = forest_percentage
            results["summary"]["deforested_percentage"] = deforested_percentage
            
            # Calculate overall percentage change
            if len(results["images"]) > 1:
                first_forest_percentage = results["images"][0]["forest_percentage"]
                last_forest_percentage = results["images"][-1]["forest_percentage"]
                results["summary"]["percentage_change"] = ((last_forest_percentage - first_forest_percentage) / first_forest_percentage) * 100
            
            # Determine overall severity
            if deforested_percentage > 15:
                results["summary"]["severity"] = "high"
            elif deforested_percentage > 8:
                results["summary"]["severity"] = "medium"
            else:
                results["summary"]["severity"] = "low"
        
        return results
    
    def detect_regrowth(self, image_paths):
        """
        Detect forest regrowth in satellite images
        
        Args:
            image_paths (list): List of paths to satellite images
            
        Returns:
            dict: Results of regrowth detection
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        results = {
            "images": [],
            "summary": {
                "total_area": 0,
                "forest_area": 0,
                "regrowth_area": 0,
                "percentage_change": 0,
                "severity": "low"
            }
        }
        
        total_forest_area = 0
        total_regrowth_area = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load and preprocess the image
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError(f"Could not load image: {image_path}")
                
                height, width = img.shape[:2]
                total_pixels = height * width
                
                # In a real implementation, you would use the model to make predictions
                # For demonstration, we'll simulate the results
                np.random.seed(i + 100)  # Different seed for regrowth
                
                # Simulate forest and regrowth areas
                forest_percentage = np.random.uniform(0.5, 0.9)
                regrowth_percentage = np.random.uniform(0.02, 0.15)
                
                # Ensure they don't overlap too much
                if forest_percentage + regrowth_percentage > 0.95:
                    regrowth_percentage = 0.95 - forest_percentage
                
                forest_area = int(forest_percentage * total_pixels)
                regrowth_area = int(regrowth_percentage * total_pixels)
                
                total_forest_area += forest_area
                total_regrowth_area += regrowth_area
                
                # Determine severity (of previous deforestation)
                if regrowth_percentage < 0.05:
                    severity = "high"  # Low regrowth indicates severe previous deforestation
                elif regrowth_percentage < 0.1:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Create a mock segmentation map
                segmentation_map = np.zeros((height, width), dtype=np.uint8)
                
                # Randomly place forest and regrowth areas
                forest_mask = np.random.random((height, width)) < forest_percentage
                regrowth_mask = np.random.random((height, width)) < regrowth_percentage
                
                # Ensure regrowth areas are not in forest areas (they are newly forested)
                regrowth_mask = regrowth_mask & ~forest_mask
                
                segmentation_map[forest_mask] = 1  # Forest
                segmentation_map[regrowth_mask] = 3  # Regrowth
                
                # Save the segmentation map
                segmentation_path = image_path.replace('.', '_regrowth.')
                cv2.imwrite(segmentation_path, segmentation_map * 85)  # Different value for regrowth
                
                # Calculate percentage change (compared to previous image if available)
                percentage_change = 0
                if i > 0:
                    prev_forest_percentage = results["images"][i-1]["forest_percentage"]
                    percentage_change = ((forest_percentage - prev_forest_percentage) / prev_forest_percentage) * 100
                
                # Add image results
                results["images"].append({
                    "image_path": image_path,
                    "segmentation_path": segmentation_path,
                    "width": width,
                    "height": height,
                    "total_pixels": total_pixels,
                    "forest_area": forest_area,
                    "forest_percentage": forest_percentage,
                    "regrowth_area": regrowth_area,
                    "regrowth_percentage": regrowth_percentage,
                    "percentage_change": percentage_change,
                    "severity": severity
                })
                
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                results["images"].append({
                    "image_path": image_path,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        results["summary"]["total_area"] = sum(img.get("total_pixels", 0) for img in results["images"])
        results["summary"]["forest_area"] = total_forest_area
        results["summary"]["regrowth_area"] = total_regrowth_area
        
        if results["summary"]["total_area"] > 0:
            forest_percentage = (total_forest_area / results["summary"]["total_area"]) * 100
            regrowth_percentage = (total_regrowth_area / results["summary"]["total_area"]) * 100
            
            results["summary"]["forest_percentage"] = forest_percentage
            results["summary"]["regrowth_percentage"] = regrowth_percentage
            
            # Calculate overall percentage change
            if len(results["images"]) > 1:
                first_forest_percentage = results["images"][0]["forest_percentage"]
                last_forest_percentage = results["images"][-1]["forest_percentage"]
                results["summary"]["percentage_change"] = ((last_forest_percentage - first_forest_percentage) / first_forest_percentage) * 100
            
            # Determine overall severity
            if regrowth_percentage < 5:
                results["summary"]["severity"] = "high"
            elif regrowth_percentage < 10:
                results["summary"]["severity"] = "medium"
            else:
                results["summary"]["severity"] = "low"
        
        return results
    
    def assess_forest_health(self, image_paths):
        """
        Assess forest health in satellite images
        
        Args:
            image_paths (list): List of paths to satellite images
            
        Returns:
            dict: Results of forest health assessment
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        results = {
            "images": [],
            "summary": {
                "total_area": 0,
                "healthy_area": 0,
                "stressed_area": 0,
                "degraded_area": 0,
                "overall_health": "good"
            }
        }
        
        total_healthy_area = 0
        total_stressed_area = 0
        total_degraded_area = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load and preprocess the image
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError(f"Could not load image: {image_path}")
                
                height, width = img.shape[:2]
                total_pixels = height * width
                
                # In a real implementation, you would use the model to make predictions
                # For demonstration, we'll simulate the results
                np.random.seed(i + 200)  # Different seed for health assessment
                
                # Simulate forest health areas
                healthy_percentage = np.random.uniform(0.4, 0.7)
                stressed_percentage = np.random.uniform(0.1, 0.3)
                degraded_percentage = np.random.uniform(0.05, 0.2)
                
                # Ensure they don't overlap too much
                total = healthy_percentage + stressed_percentage + degraded_percentage
                if total > 0.95:
                    scale = 0.95 / total
                    healthy_percentage *= scale
                    stressed_percentage *= scale
                    degraded_percentage *= scale
                
                healthy_area = int(healthy_percentage * total_pixels)
                stressed_area = int(stressed_percentage * total_pixels)
                degraded_area = int(degraded_percentage * total_pixels)
                
                total_healthy_area += healthy_area
                total_stressed_area += stressed_area
                total_degraded_area += degraded_area
                
                # Determine overall health
                if healthy_percentage > 0.6:
                    health = "good"
                elif healthy_percentage > 0.4:
                    health = "fair"
                else:
                    health = "poor"
                
                # Create a mock health map
                health_map = np.zeros((height, width), dtype=np.uint8)
                
                # Randomly place health areas
                healthy_mask = np.random.random((height, width)) < healthy_percentage
                stressed_mask = np.random.random((height, width)) < stressed_percentage
                degraded_mask = np.random.random((height, width)) < degraded_percentage
                
                # Ensure masks don't overlap
                stressed_mask = stressed_mask & ~healthy_mask
                degraded_mask = degraded_mask & ~healthy_mask & ~stressed_mask
                
                health_map[healthy_mask] = 1  # Healthy
                health_map[stressed_mask] = 2  # Stressed
                health_map[degraded_mask] = 3  # Degraded
                
                # Save the health map
                health_map_path = image_path.replace('.', '_health.')
                cv2.imwrite(health_map_path, health_map * 85)  # Different values for different health levels
                
                # Add image results
                results["images"].append({
                    "image_path": image_path,
                    "health_map_path": health_map_path,
                    "width": width,
                    "height": height,
                    "total_pixels": total_pixels,
                    "healthy_area": healthy_area,
                    "healthy_percentage": healthy_percentage,
                    "stressed_area": stressed_area,
                    "stressed_percentage": stressed_percentage,
                    "degraded_area": degraded_area,
                    "degraded_percentage": degraded_percentage,
                    "overall_health": health
                })
                
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                results["images"].append({
                    "image_path": image_path,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        results["summary"]["total_area"] = sum(img.get("total_pixels", 0) for img in results["images"])
        results["summary"]["healthy_area"] = total_healthy_area
        results["summary"]["stressed_area"] = total_stressed_area
        results["summary"]["degraded_area"] = total_degraded_area
        
        if results["summary"]["total_area"] > 0:
            healthy_percentage = (total_healthy_area / results["summary"]["total_area"]) * 100
            stressed_percentage = (total_stressed_area / results["summary"]["total_area"]) * 100
            degraded_percentage = (total_degraded_area / results["summary"]["total_area"]) * 100
            
            results["summary"]["healthy_percentage"] = healthy_percentage
            results["summary"]["stressed_percentage"] = stressed_percentage
            results["summary"]["degraded_percentage"] = degraded_percentage
            
            # Determine overall health
            if healthy_percentage > 60:
                results["summary"]["overall_health"] = "good"
            elif healthy_percentage > 40:
                results["summary"]["overall_health"] = "fair"
            else:
                results["summary"]["overall_health"] = "poor"
        
        return results
    
    def detect_fire_damage(self, image_paths):
        """
        Detect fire damage in satellite images
        
        Args:
            image_paths (list): List of paths to satellite images
            
        Returns:
            dict: Results of fire damage detection
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        results = {
            "images": [],
            "summary": {
                "total_area": 0,
                "burned_area": 0,
                "unburned_area": 0,
                "burn_severity": {
                    "low": 0,
                    "medium": 0,
                    "high": 0
                },
                "overall_damage": "low"
            }
        }
        
        total_burned_area = 0
        total_unburned_area = 0
        total_low_severity = 0
        total_medium_severity = 0
        total_high_severity = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load and preprocess the image
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError(f"Could not load image: {image_path}")
                
                height, width = img.shape[:2]
                total_pixels = height * width
                
                # In a real implementation, you would use the model to make predictions
                # For demonstration, we'll simulate the results
                np.random.seed(i + 300)  # Different seed for fire damage
                
                # Simulate burned and unburned areas
                burned_percentage = np.random.uniform(0.05, 0.4)
                unburned_percentage = 1 - burned_percentage
                
                burned_area = int(burned_percentage * total_pixels)
                unburned_area = int(unburned_percentage * total_pixels)
                
                total_burned_area += burned_area
                total_unburned_area += unburned_area
                
                # Simulate burn severity within burned areas
                low_severity_percentage = np.random.uniform(0.2, 0.5)
                medium_severity_percentage = np.random.uniform(0.2, 0.5)
                high_severity_percentage = 1 - low_severity_percentage - medium_severity_percentage
                
                low_severity_area = int(low_severity_percentage * burned_area)
                medium_severity_area = int(medium_severity_percentage * burned_area)
                high_severity_area = burned_area - low_severity_area - medium_severity_area
                
                total_low_severity += low_severity_area
                total_medium_severity += medium_severity_area
                total_high_severity += high_severity_area
                
                # Determine overall damage
                if burned_percentage > 0.3:
                    damage = "high"
                elif burned_percentage > 0.15:
                    damage = "medium"
                else:
                    damage = "low"
                
                # Create a mock burn severity map
                burn_map = np.zeros((height, width), dtype=np.uint8)
                
                # Randomly place burned areas with severity
                burned_mask = np.random.random((height, width)) < burned_percentage
                
                # Within burned areas, assign severity
                burn_severity = np.random.random((height, width))
                low_severity_mask = (burn_severity < low_severity_percentage) & burned_mask
                medium_severity_mask = (burn_severity >= low_severity_percentage) & (burn_severity < low_severity_percentage + medium_severity_percentage) & burned_mask
                high_severity_mask = (burn_severity >= low_severity_percentage + medium_severity_percentage) & burned_mask
                
                burn_map[low_severity_mask] = 1  # Low severity
                burn_map[medium_severity_mask] = 2  # Medium severity
                burn_map[high_severity_mask] = 3  # High severity
                
                # Save the burn map
                burn_map_path = image_path.replace('.', '_burn.')
                cv2.imwrite(burn_map_path, burn_map * 85)  # Different values for different severity levels
                
                # Add image results
                results["images"].append({
                    "image_path": image_path,
                    "burn_map_path": burn_map_path,
                    "width": width,
                    "height": height,
                    "total_pixels": total_pixels,
                    "burned_area": burned_area,
                    "burned_percentage": burned_percentage,
                    "unburned_area": unburned_area,
                    "unburned_percentage": unburned_percentage,
                    "burn_severity": {
                        "low": {
                            "area": low_severity_area,
                            "percentage": (low_severity_area / total_pixels) * 100
                        },
                        "medium": {
                            "area": medium_severity_area,
                            "percentage": (medium_severity_area / total_pixels) * 100
                        },
                        "high": {
                            "area": high_severity_area,
                            "percentage": (high_severity_area / total_pixels) * 100
                        }
                    },
                    "overall_damage": damage
                })
                
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                results["images"].append({
                    "image_path": image_path,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        results["summary"]["total_area"] = sum(img.get("total_pixels", 0) for img in results["images"])
        results["summary"]["burned_area"] = total_burned_area
        results["summary"]["unburned_area"] = total_unburned_area
        
        if results["summary"]["total_area"] > 0:
            burned_percentage = (total_burned_area / results["summary"]["total_area"]) * 100
            unburned_percentage = (total_unburned_area / results["summary"]["total_area"]) * 100
            
            results["summary"]["burned_percentage"] = burned_percentage
            results["summary"]["unburned_percentage"] = unburned_percentage
            
            # Calculate burn severity percentages
            if total_burned_area > 0:
                results["summary"]["burn_severity"]["low"] = (total_low_severity / total_burned_area) * 100
                results["summary"]["burn_severity"]["medium"] = (total_medium_severity / total_burned_area) * 100
                results["summary"]["burn_severity"]["high"] = (total_high_severity / total_burned_area) * 100
            
            # Determine overall damage
            if burned_percentage > 30:
                results["summary"]["overall_damage"] = "high"
            elif burned_percentage > 15:
                results["summary"]["overall_damage"] = "medium"
            else:
                results["summary"]["overall_damage"] = "low"
        
        return results