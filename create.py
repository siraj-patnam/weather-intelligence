#!/usr/bin/env python3
"""
Weather Intelligence Hub - Project Setup Script
Creates all required files and directories
"""

import os
from pathlib import Path

def create_project_structure():
    """Create the complete project structure"""
    
    # Define all directories to create
    directories = [
        "services",
        "utils", 
        "static",
        "static/weather_icons"
    ]
    
    # Define all files to create
    files = [
        # Main files
        "app.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        
        # Services
        "services/__init__.py",
        "services/weather_service.py",
        "services/location_service.py",
        "services/database_service.py",
        "services/ai_assistant.py",
        
        # Utils
        "utils/__init__.py",
        "utils/helpers.py",
        "utils/map_utils.py",
        "utils/validators.py"
    ]
    
    print("🚀 Creating Weather Intelligence Hub project structure...")
    print("=" * 60)
    
    # Create directories
    print("\n📁 Creating directories:")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}/")
    
    # Create files
    print("\n📄 Creating files:")
    for file_path in files:
        Path(file_path).touch()
        print(f"✅ {file_path}")
    
    # Create .env from .env.example if it doesn't exist
    if not Path(".env").exists():
        Path(".env").touch()
        print("✅ .env")
    
    print("\n" + "=" * 60)
    print("🎉 Project structure created successfully!")
    print("\n📋 Next steps:")
    print("1. Add your API keys to .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Add your code to the created files")
    print("4. Run the app: streamlit run app.py")
    print("\n🌍 Happy coding!")

if __name__ == "__main__":
    create_project_structure()