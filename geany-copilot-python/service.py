#!/usr/bin/env python3
"""
Geany Copilot Python Service

A standalone Python service that provides AI-powered code assistance
and copywriting features. This service can be used independently or
as a backend for the Lua plugin.

This service provides:
- HTTP API for code assistance
- WebSocket support for real-time communication
- Advanced agent capabilities
- Multi-turn conversations
- Context-aware assistance

Author: Geany Copilot Team
Version: 2.0.0
License: MIT
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    import requests
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available. Install with: pip install flask flask-cors requests")
    FLASK_AVAILABLE = False

from core.config import ConfigManager
from core.agent import AIAgent
from agents.code_assistant import CodeAssistant
from agents.copywriter import CopywriterAssistant
from utils.logging_setup import setup_plugin_logging

# Setup logging
logger = setup_plugin_logging(debug=True)

class GeanyCopilotService:
    """
    Standalone service for Geany Copilot functionality.
    
    Provides HTTP API endpoints for code assistance and copywriting,
    allowing integration with Lua plugins or external tools.
    """
    
    def __init__(self, port: int = 8765, host: str = "localhost"):
        self.port = port
        self.host = host
        self.app = None
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.ai_agent = AIAgent(self.config_manager)
        self.code_assistant = CodeAssistant(self.ai_agent, self.config_manager)
        self.copywriter = CopywriterAssistant(self.ai_agent, self.config_manager)
        
        if FLASK_AVAILABLE:
            self.setup_flask_app()
    
    def setup_flask_app(self):
        """Setup Flask application with API endpoints."""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for cross-origin requests
        
        @self.app.route('/')
        def index():
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Geany Copilot Service</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .method { color: #007acc; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>🚀 Geany Copilot Service</h1>
                <p>AI-powered code assistance and copywriting service</p>
                <p><strong>Version:</strong> 2.0.0</p>
                <p><strong>Status:</strong> Running on {{ host }}:{{ port }}</p>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/code-assist</code><br>
                    Get AI-powered code assistance
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/copywriter</code><br>
                    Get AI-powered copywriting assistance
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/api/config</code><br>
                    Get current configuration
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/config</code><br>
                    Update configuration
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/api/health</code><br>
                    Health check endpoint
                </div>
            </body>
            </html>
            """, host=self.host, port=self.port)
        
        @self.app.route('/api/health')
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": "geany-copilot",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get current configuration."""
            try:
                config = self.config_manager.get_all_settings()
                # Remove sensitive information
                safe_config = {k: v for k, v in config.items() if 'key' not in k.lower()}
                return jsonify({"config": safe_config})
            except Exception as e:
                logger.error(f"Error getting config: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update configuration."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Update configuration
                for key, value in data.items():
                    self.config_manager.set_setting(key, value)
                
                return jsonify({"message": "Configuration updated successfully"})
            except Exception as e:
                logger.error(f"Error updating config: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/code-assist', methods=['POST'])
        def code_assist():
            """Provide AI-powered code assistance."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                prompt = data.get('prompt', '')
                code = data.get('code', '')
                filename = data.get('filename', '')
                filetype = data.get('filetype', '')
                
                if not prompt:
                    return jsonify({"error": "Prompt is required"}), 400
                
                # Create context
                context = {
                    'filename': filename,
                    'filetype': filetype,
                    'selected_text': code,
                    'prompt': prompt
                }
                
                # Get response from code assistant
                response = self.code_assistant.process_request(context)
                
                return jsonify({
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in code assistance: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/copywriter', methods=['POST'])
        def copywriter():
            """Provide AI-powered copywriting assistance."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                text = data.get('text', '')
                prompt = data.get('prompt', 'Improve this text')
                
                if not text:
                    return jsonify({"error": "Text is required"}), 400
                
                # Create context
                context = {
                    'selected_text': text,
                    'prompt': prompt
                }
                
                # Get response from copywriter
                response = self.copywriter.process_request(context)
                
                return jsonify({
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in copywriting: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run_flask_service(self):
        """Run the Flask service."""
        if not FLASK_AVAILABLE:
            logger.error("Flask is not available. Cannot start HTTP service.")
            return
        
        logger.info(f"Starting Geany Copilot Service on {self.host}:{self.port}")
        logger.info(f"Access the service at: http://{self.host}:{self.port}")
        
        try:
            self.app.run(host=self.host, port=self.port, debug=False)
        except Exception as e:
            logger.error(f"Error starting Flask service: {e}")
    
    def run_cli_mode(self):
        """Run in CLI mode for direct interaction."""
        logger.info("Starting Geany Copilot in CLI mode")
        logger.info("Type 'help' for available commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\nGeany Copilot> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    print("""
Available commands:
  code <prompt>     - Get code assistance
  copy <text>       - Get copywriting help
  config            - Show configuration
  health            - Show service status
  help              - Show this help
  quit              - Exit the service
                    """)
                elif command.startswith('code '):
                    prompt = command[5:]
                    context = {'prompt': prompt, 'selected_text': ''}
                    response = self.code_assistant.process_request(context)
                    print(f"\nResponse: {response}")
                elif command.startswith('copy '):
                    text = command[5:]
                    context = {'selected_text': text, 'prompt': 'Improve this text'}
                    response = self.copywriter.process_request(context)
                    print(f"\nResponse: {response}")
                elif command.lower() == 'config':
                    config = self.config_manager.get_all_settings()
                    safe_config = {k: v for k, v in config.items() if 'key' not in k.lower()}
                    print(f"\nConfiguration: {json.dumps(safe_config, indent=2)}")
                elif command.lower() == 'health':
                    print(f"\nService: Geany Copilot v2.0.0")
                    print(f"Status: Running")
                    print(f"Time: {datetime.now().isoformat()}")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                print(f"Error: {e}")
        
        logger.info("Geany Copilot CLI mode stopped")


def main():
    """Main entry point for the service."""
    parser = argparse.ArgumentParser(description="Geany Copilot Python Service")
    parser.add_argument('--port', type=int, default=8765, help='Port to run the service on')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind the service to')
    parser.add_argument('--mode', choices=['http', 'cli'], default='http', help='Service mode')
    
    args = parser.parse_args()
    
    service = GeanyCopilotService(port=args.port, host=args.host)
    
    if args.mode == 'http':
        service.run_flask_service()
    else:
        service.run_cli_mode()


if __name__ == "__main__":
    main()
