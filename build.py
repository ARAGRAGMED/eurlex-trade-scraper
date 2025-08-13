#!/usr/bin/env python3
"""
Build script for preparing the EUR-Lex Trade Scraper for Vercel deployment.
"""

import shutil
import os
from pathlib import Path

def main():
    """Prepare the project for Vercel deployment."""
    print("🇪🇺 Preparing EUR-Lex Trade Scraper for Vercel deployment...")
    
    project_root = Path(__file__).parent
    static_dir = project_root / "static"
    src_web_dir = project_root / "src" / "web"
    data_dir = project_root / "data"
    
    # Ensure static directory exists
    static_dir.mkdir(exist_ok=True)
    print(f"✅ Created static directory: {static_dir}")
    
    # Copy web files to static directory
    if src_web_dir.exists():
        for file in src_web_dir.glob("*"):
            if file.is_file():
                dest = static_dir / file.name
                shutil.copy2(file, dest)
                print(f"✅ Copied {file.name} to static/")
    
    # Create empty data structure for initial deployment
    static_data_dir = static_dir / "data"
    static_data_dir.mkdir(exist_ok=True)
    
    # Create empty results file
    results_file = static_data_dir / "results-2025.json"
    with open(results_file, 'w') as f:
        f.write('[]')
    
    # Create empty state file
    state_file = static_data_dir / "state.json"
    with open(state_file, 'w') as f:
        f.write('{"last_checked_date": null, "last_run": null, "total_documents": 0}')
    
    print(f"✅ Created empty data structure in static/data/")
    
    # Verify required files exist
    required_files = [
        "vercel.json",
        "requirements.txt",
        "api/index.py",
        "static/index.html",
        "static/app.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    print("\n🎉 Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Initialize git repository: git init")
    print("2. Add files: git add .")
    print("3. Commit: git commit -m 'Initial commit'")
    print("4. Push to GitHub: git remote add origin <your-repo-url> && git push -u origin main")
    print("5. Connect to Vercel and deploy")
    print("\n🔧 Environment Variables to set in Vercel:")
    print("   - EURLEX_USERNAME=your_eurlex_username")
    print("   - EURLEX_PASSWORD=your_eurlex_password")
    print("   - EURLEX_WSDL_URL=https://eur-lex.europa.eu/EURLexWebService?wsdl")
    print("   - DATA_DIR=/tmp/eurlex-data")
    print("   - LOG_LEVEL=INFO")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
