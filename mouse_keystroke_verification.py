# This is a standalone version of the bot detection logic
# For a complete integration, this would be incorporated into app.py

import numpy as np
import time
from flask import Flask, request, jsonify # type: ignore

class BehaviorVerification:
    def __init__(self):
        self.velocity_threshold = 2.5
        self.typing_speed_threshold = 8.0  # chars per second
        self.typing_variability_threshold = 0.3
    
    def analyze_mouse_movement(self, positions, timestamps):
        """
        Analyze mouse movement patterns to detect bots
        
        Args:
            positions: List of [x, y] coordinates
            timestamps: List of timestamps in milliseconds
            
        Returns:
            dict: Analysis results with detection status
        """
        # Convert timestamps to seconds
        timestamps = [t/1000 for t in timestamps]
        
        # Need enough data points
        if len(positions) < 3:
            return {"is_human": False, "reason": "Not enough movement data"}
        
        # Calculate velocities
        velocities = []
        for i in range(1, len(positions)):
            dt = timestamps[i] - timestamps[i-1]
            if dt == 0:
                continue
                
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            velocity = np.sqrt(dx**2 + dy**2) / dt
            velocities.append(velocity)
        
        if not velocities:
            return {"is_human": False, "reason": "Could not calculate velocities"}
            
        # Calculate standard deviation of velocities (natural human movements have higher variability)
        velocity_std = np.std(velocities)
        
        is_human = velocity_std >= self.velocity_threshold
        
        return {
            "is_human": is_human,
            "score": velocity_std,
            "threshold": self.velocity_threshold,
            "reason": "Movement pattern analysis" 
        }
    
    def analyze_typing_pattern(self, keystroke_times, text_length, total_time):
        """
        Analyze typing patterns to detect bots
        
        Args:
            keystroke_times: List of keystroke timestamps
            text_length: Length of typed text
            total_time: Total typing time in seconds
            
        Returns:
            dict: Analysis results with detection status
        """
        # Need enough keystrokes
        if len(keystroke_times) < 3:
            return {"is_human": False, "reason": "Not enough keystroke data"}
        
        # Calculate typing speed (chars per second)
        typing_speed = text_length / total_time
        
        # Calculate keystroke timing variability
        keystroke_intervals = [keystroke_times[i] - keystroke_times[i-1] 
                              for i in range(1, len(keystroke_times))]
        
        mean_interval = np.mean(keystroke_intervals)
        std_interval = np.std(keystroke_intervals)
        
        # Coefficient of variation (higher means more human-like variability)
        variability = std_interval / mean_interval if mean_interval > 0 else 0
        
        # Check if typing pattern looks human
        is_human = (typing_speed <= self.typing_speed_threshold and 
                   variability >= self.typing_variability_threshold)
        
        return {
            "is_human": is_human,
            "typing_speed": typing_speed,
            "typing_variability": variability,
            "speed_threshold": self.typing_speed_threshold,
            "variability_threshold": self.typing_variability_threshold,
            "reason": "Typing pattern analysis"
        }

# API endpoints for verification (if using as a separate service)
if __name__ == "__main__":
    app = Flask(__name__)
    verifier = BehaviorVerification()
    
    @app.route('/api/verify-mouse-movement', methods=['POST'])
    def verify_mouse():
        data = request.json
        positions = data.get('positions', [])
        timestamps = data.get('timestamps', [])
        
        result = verifier.analyze_mouse_movement(positions, timestamps)
        return jsonify(result)
    
    @app.route('/api/verify-typing', methods=['POST'])
    def verify_typing():
        data = request.json
        keystroke_times = data.get('keystrokeTimes', [])
        text_length = data.get('textLength', 0)
        total_time = data.get('totalTime', 0)
        
        result = verifier.analyze_typing_pattern(keystroke_times, text_length, total_time)
        return jsonify(result)
    
    app.run(port=5001, debug=True)