"""
Ecosystem Simulation API Interface
Provides RESTful API endpoints for ecosystem simulation control and data access
"""

from flask import Flask, jsonify, request
from typing import Dict, Any, List, Optional
import json
import threading
import time

from backend.engine.simulation import SimulationEngine
from backend.models.ecosystem import EcosystemConfig


class EcosystemAPI:
    """API interface for ecosystem simulation"""
    
    def __init__(self, simulation_engine: SimulationEngine):
        """
        Initialize API interface
        
        Args:
            simulation_engine: Simulation engine instance
        """
        self.simulation_engine = simulation_engine
        self.app = Flask(__name__)
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get simulation status"""
            try:
                ecosystem_state = self.simulation_engine.get_ecosystem_state()
                
                status = {
                    'time_step': self.simulation_engine.time_step,
                    'running': True,
                    'grass_count': len([g for g in ecosystem_state['grass_list'] if g.alive]),
                    'cow_count': len([c for c in ecosystem_state['cow_list'] if c.alive]),
                    'tiger_count': len([t for t in ecosystem_state['tiger_list'] if t.alive]),
                    'total_entities': len(ecosystem_state['grass_list']) + 
                                    len(ecosystem_state['cow_list']) + 
                                    len(ecosystem_state['tiger_list'])
                }
                
                return jsonify({
                    'success': True,
                    'data': status
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/ecosystem', methods=['GET'])
        def get_ecosystem_data():
            """Get complete ecosystem data"""
            try:
                ecosystem_state = self.simulation_engine.get_ecosystem_state()
                
                # Convert entity data to serializable format
                grass_data = []
                for grass in ecosystem_state['grass_list']:
                    if grass.alive:
                        grass_data.append({
                            'id': id(grass),
                            'x': grass.x,
                            'y': grass.y,
                            'energy': grass.energy,
                            'growth_rate': grass.growth_rate
                        })
                
                cow_data = []
                for cow in ecosystem_state['cow_list']:
                    if cow.alive:
                        cow_data.append({
                            'id': id(cow),
                            'x': cow.x,
                            'y': cow.y,
                            'energy': cow.energy,
                            'age': cow.age,
                            'reproduction_cooldown': cow.reproduction_cooldown
                        })
                
                tiger_data = []
                for tiger in ecosystem_state['tiger_list']:
                    if tiger.alive:
                        tiger_data.append({
                            'id': id(tiger),
                            'x': tiger.x,
                            'y': tiger.y,
                            'energy': tiger.energy,
                            'age': tiger.age,
                            'reproduction_cooldown': tiger.reproduction_cooldown
                        })
                
                return jsonify({
                    'success': True,
                    'data': {
                        'time_step': self.simulation_engine.time_step,
                        'grass': grass_data,
                        'cows': cow_data,
                        'tigers': tiger_data
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Get simulation statistics"""
            try:
                ecosystem_state = self.simulation_engine.get_ecosystem_state()
                
                # Calculate statistics
                alive_grass = [g for g in ecosystem_state['grass_list'] if g.alive]
                alive_cows = [c for c in ecosystem_state['cow_list'] if c.alive]
                alive_tigers = [t for t in ecosystem_state['tiger_list'] if t.alive]
                
                stats = {
                    'time_step': self.simulation_engine.time_step,
                    'population': {
                        'grass': len(alive_grass),
                        'cows': len(alive_cows),
                        'tigers': len(alive_tigers)
                    },
                    'energy_stats': {
                        'grass_avg_energy': sum(g.energy for g in alive_grass) / len(alive_grass) if alive_grass else 0,
                        'cow_avg_energy': sum(c.energy for c in alive_cows) / len(alive_cows) if alive_cows else 0,
                        'tiger_avg_energy': sum(t.energy for t in alive_tigers) / len(alive_tigers) if alive_tigers else 0
                    },
                    'age_stats': {
                        'cow_avg_age': sum(c.age for c in alive_cows) / len(alive_cows) if alive_cows else 0,
                        'tiger_avg_age': sum(t.age for t in alive_tigers) / len(alive_tigers) if alive_tigers else 0
                    }
                }
                
                return jsonify({
                    'success': True,
                    'data': stats
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/reset', methods=['POST'])
        def reset_simulation():
            """Reset simulation to initial state"""
            try:
                # Get current configuration
                config = self.simulation_engine.ecosystem.config
                
                # Create new simulation engine
                self.simulation_engine = SimulationEngine(config)
                
                return jsonify({
                    'success': True,
                    'message': 'Simulation reset successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get current simulation configuration"""
            try:
                config = self.simulation_engine.ecosystem.config
                
                config_data = {
                    'world_width': config.world_width,
                    'world_height': config.world_height,
                    'initial_grass': config.initial_grass,
                    'initial_cows': config.initial_cows,
                    'initial_tigers': config.initial_tigers
                }
                
                return jsonify({
                    'success': True,
                    'data': config_data
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update simulation configuration"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No configuration data provided'
                    }), 400
                
                # Get current configuration
                current_config = self.simulation_engine.ecosystem.config
                
                # Update configuration with provided values
                new_config = EcosystemConfig(
                    world_width=data.get('world_width', current_config.world_width),
                    world_height=data.get('world_height', current_config.world_height),
                    initial_grass=data.get('initial_grass', current_config.initial_grass),
                    initial_cows=data.get('initial_cows', current_config.initial_cows),
                    initial_tigers=data.get('initial_tigers', current_config.initial_tigers)
                )
                
                # Create new simulation engine with updated configuration
                self.simulation_engine = SimulationEngine(new_config)
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        Run the API server
        
        Args:
            host: Server host address
            port: Server port
            debug: Enable debug mode
        """
        self.app.run(host=host, port=port, debug=debug)


class APIServer:
    """API server wrapper for running in separate thread"""
    
    def __init__(self, simulation_engine: SimulationEngine):
        """
        Initialize API server
        
        Args:
            simulation_engine: Simulation engine instance
        """
        self.api = EcosystemAPI(simulation_engine)
        self.server_thread = None
        self.running = False
    
    def start(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Start API server in separate thread
        
        Args:
            host: Server host address
            port: Server port
        """
        if not self.running:
            self.running = True
            self.server_thread = threading.Thread(
                target=self.api.run,
                kwargs={'host': host, 'port': port, 'debug': False}
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"API server started on http://{host}:{port}")
    
    def stop(self):
        """Stop API server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
            print("API server stopped")


# Example usage
if __name__ == "__main__":
    from backend.models.ecosystem import EcosystemConfig
    
    # Create configuration
    config = EcosystemConfig(
        world_width=800,
        world_height=600,
        initial_grass=100,
        initial_cows=20,
        initial_tigers=5
    )
    
    # Create simulation engine
    simulation_engine = SimulationEngine(config)
    
    # Create and run API
    api = EcosystemAPI(simulation_engine)
    api.run(debug=True)