document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    const map = L.map('map').setView([20.5937, 78.9629], 5); // Centered on India
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Sample deforestation data
    const deforestationData = [
        {
            name: "Western Ghats",
            coords: [10.5328, 76.2144],
            severity: "high",
            area: "1240 ha",
            change: "-5.2%"
        },
        {
            name: "Northeast Region",
            coords: [26.2006, 92.9376],
            severity: "medium",
            area: "870 ha",
            change: "-3.1%"
        },
        {
            name: "Central India",
            coords: [22.9734, 78.6569],
            severity: "low",
            area: "320 ha",
            change: "-1.2%"
        },
        {
            name: "Eastern Ghats",
            coords: [18.1124, 83.4019],
            severity: "high",
            area: "1560 ha",
            change: "-7.4%"
        },
        {
            name: "Himalayan Region",
            coords: [31.1048, 77.1734],
            severity: "medium",
            area: "680 ha",
            change: "-2.8%"
        }
    ];
    
    // Function to determine marker color based on severity
    function getMarkerColor(severity) {
        switch(severity) {
            case 'high':
                return '#f44336'; // Red
            case 'medium':
                return '#ff9800'; // Orange
            case 'low':
                return '#4caf50'; // Green
            default:
                return '#2196f3'; // Blue
        }
    }
    
    // Add markers to the map
    deforestationData.forEach(location => {
        // Create custom icon
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${getMarkerColor(location.severity)}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        // Create marker
        const marker = L.marker(location.coords, { icon: customIcon }).addTo(map);
        
        // Create popup content
        const popupContent = `
            <div class="map-popup">
                <h3>${location.name}</h3>
                <div class="popup-info">
                    <p><strong>Area Affected:</strong> ${location.area}</p>
                    <p><strong>Forest Change:</strong> <span class="${location.severity}">${location.change}</span></p>
                    <p><strong>Severity:</strong> <span class="severity-badge ${location.severity}">${location.severity.charAt(0).toUpperCase() + location.severity.slice(1)}</span></p>
                </div>
                <button class="popup-btn view-details">View Details</button>
            </div>
        `;
        
        // Add popup to marker
        marker.bindPopup(popupContent);
        
        // Add event listener to the view details button
        marker.on('popupopen', function() {
            document.querySelector('.view-details').addEventListener('click', function() {
                // Here you would normally show detailed information about this location
                console.log(`Showing details for ${location.name}`);
                
                // Scroll to the analysis section
                document.querySelector('#analysis').scrollIntoView({ behavior: 'smooth' });
            });
        });
    });
    
    // Add legend to the map
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = `
            <h4>Deforestation Severity</h4>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #f44336;"></div>
                <span>High</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #ff9800;"></div>
                <span>Medium</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #4caf50;"></div>
                <span>Low</span>
            </div>
        `;
        
        // Add styles for legend
        const style = document.createElement('style');
        style.textContent = `
            .map-legend {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .map-legend h4 {
                margin: 0 0 10px;
                font-size: 14px;
                font-weight: 600;
            }
            
            .legend-item {
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }
            
            .legend-color {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .map-popup {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-width: 200px;
            }
            
            .map-popup h3 {
                margin: 0 0 10px;
                font-size: 16px;
                color: #2e7d32;
            }
            
            .popup-info {
                margin-bottom: 10px;
            }
            
            .popup-info p {
                margin: 5px 0;
                font-size: 14px;
            }
            
            .popup-info .high {
                color: #f44336;
                font-weight: 600;
            }
            
            .popup-info .medium {
                color: #ff9800;
                font-weight: 600;
            }
            
            .popup-info .low {
                color: #4caf50;
                font-weight: 600;
            }
            
            .severity-badge {
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                color: white;
            }
            
            .severity-badge.high {
                background-color: #f44336;
            }
            
            .severity-badge.medium {
                background-color: #ff9800;
            }
            
            .severity-badge.low {
                background-color: #4caf50;
            }
            
            .popup-btn {
                background-color: #2e7d32;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                cursor: pointer;
                width: 100%;
                transition: background-color 0.2s;
            }
            
            .popup-btn:hover {
                background-color: #1b5e20;
            }
        `;
        
        if (!document.querySelector('#map-legend-styles')) {
            style.id = 'map-legend-styles';
            document.head.appendChild(style);
        }
        
        return div;
    };
    
    legend.addTo(map);
    
    // Map view buttons functionality
    const currentViewBtn = document.getElementById('currentView');
    const historicalViewBtn = document.getElementById('historicalView');
    const comparisonViewBtn = document.getElementById('comparisonView');
    
    // Function to update map based on selected view
    function updateMapView(viewType) {
        // Here you would normally load different data layers based on the view type
        console.log(`Updating map view to: ${viewType}`);
        
        // For demonstration, we'll just show a notification
        let message = '';
        switch(viewType) {
            case 'current':
                message = 'Showing current deforestation data';
                break;
            case 'historical':
                message = 'Showing historical deforestation data';
                break;
            case 'comparison':
                message = 'Showing comparison view';
                break;
        }
        
        // Create a temporary notification on the map
        const notification = L.divNotification({
            className: 'map-notification',
            content: message,
            position: 'topright',
            duration: 3000
        });
        
        // Add notification styles if they don't exist
        if (!document.querySelector('#map-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'map-notification-styles';
            style.textContent = `
                .map-notification {
                    background-color: rgba(46, 125, 50, 0.9);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 4px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 14px;
                    z-index: 1000;
                    animation: fadeIn 0.3s ease;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add notification to map
        map.addNotification(notification);
    }
    
    // Add event listeners to view buttons
    currentViewBtn.addEventListener('click', function() {
        updateMapView('current');
    });
    
    historicalViewBtn.addEventListener('click', function() {
        updateMapView('historical');
    });
    
    comparisonViewBtn.addEventListener('click', function() {
        updateMapView('comparison');
    });
    
    // Add a simple notification method to Leaflet map
    L.Map.include({
        addNotification: function(notification) {
            const container = this.getContainer();
            const notificationEl = document.createElement('div');
            notificationEl.className = notification.className || 'map-notification';
            notificationEl.innerHTML = notification.content;
            notificationEl.style.position = 'absolute';
            notificationEl.style.zIndex = '1000';
            
            // Set position
            switch(notification.position) {
                case 'topleft':
                    notificationEl.style.top = '10px';
                    notificationEl.style.left = '10px';
                    break;
                case 'topright':
                    notificationEl.style.top = '10px';
                    notificationEl.style.right = '10px';
                    break;
                case 'bottomleft':
                    notificationEl.style.bottom = '10px';
                    notificationEl.style.left = '10px';
                    break;
                case 'bottomright':
                    notificationEl.style.bottom = '10px';
                    notificationEl.style.right = '10px';
                    break;
                default:
                    notificationEl.style.top = '10px';
                    notificationEl.style.left = '50%';
                    notificationEl.style.transform = 'translateX(-50%)';
            }
            
            container.appendChild(notificationEl);
            
            // Remove notification after duration
            if (notification.duration) {
                setTimeout(() => {
                    notificationEl.style.opacity = '0';
                    notificationEl.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => {
                        container.removeChild(notificationEl);
                    }, 500);
                }, notification.duration);
            }
        }
    });
    
    // Add a divNotification method to Leaflet
    L.divNotification = function(options) {
        return options;
    };
    
    // Add heatmap layer (would require additional library in a real implementation)
    // This is just a placeholder for demonstration
    function addHeatmap() {
        // In a real implementation, you would use a library like leaflet.heat
        // For now, we'll just log that this would add a heatmap
        console.log('Heatmap layer would be added here');
    }
    
    // Add a function to fit map to show all markers
    function fitMapToMarkers() {
        const group = new L.featureGroup(
            deforestationData.map(location => L.marker(location.coords))
        );
        map.fitBounds(group.getBounds().pad(0.1));
    }
    
    // Fit map to show all markers on load
    setTimeout(fitMapToMarkers, 500);
    
    // Add event listener to window resize to adjust map
    window.addEventListener('resize', function() {
        map.invalidateSize();
    });
});