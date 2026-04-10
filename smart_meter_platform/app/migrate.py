#!/usr/bin/env python3
"""
Smart Meter Platform - Production Upgrade Migration Script
Automatically backs up old files and deploys enhanced system
"""

import os
import shutil
import sys
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def backup_file(filepath, backup_dir):
    """Backup a file to backup directory"""
    if not os.path.exists(filepath):
        print_warning(f"File not found (will be created): {filepath}")
        return True
    
    try:
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, filename)
        shutil.copy2(filepath, backup_path)
        print_success(f"Backed up: {filename}")
        return True
    except Exception as e:
        print_error(f"Backup failed for {filepath}: {e}")
        return False

def deploy_file(source, destination):
    """Deploy enhanced file"""
    try:
        shutil.copy2(source, destination)
        filename = os.path.basename(destination)
        print_success(f"Deployed: {filename}")
        return True
    except Exception as e:
        print_error(f"Deploy failed for {destination}: {e}")
        return False

def main():
    print_header("SMART METER PLATFORM - PRODUCTION UPGRADE")
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Assume script in outputs/
    app_dir = os.path.join(project_root, 'app')
    
    print_info(f"Project root: {project_root}")
    print_info(f"App directory: {app_dir}")
    
    # Verify app directory exists
    if not os.path.exists(app_dir):
        print_error(f"App directory not found: {app_dir}")
        print_info("Please run this script from the outputs directory")
        sys.exit(1)
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(project_root, f'backup_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    print_success(f"Created backup directory: {backup_dir}")
    
    # Files to migrate
    files_to_migrate = [
        'ai_model.py',
        'models.py',
        '__init__.py',
        'utils.py'
    ]
    
    # Phase 1: Backup
    print_header("PHASE 1: BACKING UP EXISTING FILES")
    backup_success = True
    for filename in files_to_migrate:
        filepath = os.path.join(app_dir, filename)
        if not backup_file(filepath, backup_dir):
            backup_success = False
    
    if not backup_success:
        print_error("Backup phase failed. Aborting migration.")
        sys.exit(1)
    
    # Phase 2: Deploy
    print_header("PHASE 2: DEPLOYING ENHANCED FILES")
    deploy_success = True
    for filename in files_to_migrate:
        source = os.path.join(script_dir, filename)
        destination = os.path.join(app_dir, filename)
        
        if not os.path.exists(source):
            print_error(f"Source file not found: {source}")
            deploy_success = False
            continue
        
        if not deploy_file(source, destination):
            deploy_success = False
    
    if not deploy_success:
        print_error("Deployment phase failed.")
        print_warning("Restore from backup if needed:")
        print_info(f"  cp {backup_dir}/* {app_dir}/")
        sys.exit(1)
    
    # Phase 3: Cleanup old model
    print_header("PHASE 3: CLEANUP & INITIALIZATION")
    old_model = os.path.join(app_dir, 'lstm_classifier.h5')
    if os.path.exists(old_model):
        try:
            # Backup old model too
            shutil.copy2(old_model, os.path.join(backup_dir, 'lstm_classifier.h5'))
            os.remove(old_model)
            print_success("Removed old binary classifier model")
            print_info("New multi-class model will be trained on first run")
        except Exception as e:
            print_warning(f"Could not remove old model: {e}")
    
    # Phase 4: Verify
    print_header("PHASE 4: VERIFICATION")
    all_verified = True
    for filename in files_to_migrate:
        filepath = os.path.join(app_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print_success(f"{filename}: {size:,} bytes")
        else:
            print_error(f"{filename}: NOT FOUND")
            all_verified = False
    
    # Final status
    print_header("MIGRATION COMPLETE")
    if all_verified:
        print_success("All files deployed successfully!")
        print_info("\nNext steps:")
        print_info("1. Review changes: diff app/ backup_*/")
        print_info("2. Start application: python run.py")
        print_info("3. Monitor console for training logs")
        print_info("4. Verify dashboard shows varied alerts")
        print_info(f"\n📁 Backup location: {backup_dir}")
        print_info("💾 Restore command (if needed):")
        print_info(f"   cp {backup_dir}/* {app_dir}/")
    else:
        print_error("Migration completed with errors")
        print_warning("Review errors above and restore from backup if needed")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
