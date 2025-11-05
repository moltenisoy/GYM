#!/usr/bin/env python3
"""
Test script to verify the complete GYM system functionality.
Tests database, API, and authentication flow.
"""

import sys
import time
import requests
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    """Print a colored header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print info message."""
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_database():
    """Test database operations."""
    print_header("TEST 1: Database Operations")
    
    try:
        import madre_db
        
        # Test getting users
        users = madre_db.get_all_users()
        print_success(f"Database connection OK - Found {len(users)} users")
        
        # Verify each user has required data
        for user in users:
            username = user['username']
            user_id = user['id']
            
            # Check profile
            profile_photo = madre_db.get_user_profile_photo(user_id)
            if profile_photo:
                print_success(f"  {username}: Profile photo OK")
            else:
                print_error(f"  {username}: No profile photo")
            
            # Check training schedule
            schedule = madre_db.get_training_schedule(user_id)
            if schedule:
                print_success(f"  {username}: Training schedule OK ({schedule['mes']} {schedule['ano']})")
            else:
                print_error(f"  {username}: No training schedule")
            
            # Check gallery
            gallery = madre_db.get_photo_gallery(user_id)
            if gallery:
                print_success(f"  {username}: Photo gallery OK ({len(gallery)} photos)")
            else:
                print_error(f"  {username}: No gallery photos")
        
        # Test authentication
        print_info("\nTesting authentication...")
        success, user_data = madre_db.authenticate_user('juan_perez', 'gym2024')
        if success:
            print_success("Authentication with correct password: OK")
        else:
            print_error("Authentication with correct password: FAILED")
        
        success, user_data = madre_db.authenticate_user('juan_perez', 'wrong_password')
        if not success:
            print_success("Authentication with wrong password correctly rejected")
        else:
            print_error("Authentication with wrong password: SECURITY ISSUE")
        
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def test_api_server(base_url='http://127.0.0.1:8000'):
    """Test API server endpoints."""
    print_header("TEST 2: API Server Endpoints")
    
    try:
        # Test 1: Root endpoint
        print_info("Testing root endpoint...")
        response = requests.get(f'{base_url}/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Root endpoint OK - Version: {data.get('version', 'N/A')}")
        else:
            print_error(f"Root endpoint failed: {response.status_code}")
            return False
        
        # Test 2: Authentication
        print_info("\nTesting authentication endpoint...")
        response = requests.post(
            f'{base_url}/autorizar',
            json={'username': 'juan_perez', 'password': 'gym2024'},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Authentication OK - User: {data.get('nombre_completo', 'N/A')}")
        else:
            print_error(f"Authentication failed: {response.status_code}")
            return False
        
        # Test 3: Wrong password
        print_info("Testing wrong password rejection...")
        response = requests.post(
            f'{base_url}/autorizar',
            json={'username': 'juan_perez', 'password': 'wrong'},
            timeout=5
        )
        if response.status_code == 401:
            print_success("Wrong password correctly rejected (401)")
        else:
            print_error(f"Wrong password not rejected properly: {response.status_code}")
        
        # Test 4: Blocked user
        print_info("Testing blocked user...")
        response = requests.post(
            f'{base_url}/autorizar',
            json={'username': 'carlos_rodriguez', 'password': 'trainer123'},
            timeout=5
        )
        if response.status_code == 403:
            print_success("Blocked user correctly denied (403)")
        else:
            print_error(f"Blocked user not denied properly: {response.status_code}")
        
        # Test 5: Sync validation
        print_info("\nTesting sync validation...")
        response = requests.get(
            f'{base_url}/validar_sync?usuario=juan_perez',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            bloqueado = data.get('bloqueado', True)
            if not bloqueado:
                print_success(f"Sync validation OK - Status: {data.get('mensaje', 'N/A')}")
            else:
                print_error("User should not be blocked after recent sync")
        else:
            print_error(f"Sync validation failed: {response.status_code}")
        
        # Test 6: Complete sync
        print_info("\nTesting complete data sync...")
        response = requests.get(
            f'{base_url}/sincronizar_datos?usuario=juan_perez',
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            usuario = data.get('usuario', {})
            schedule = data.get('training_schedule')
            gallery = data.get('photo_gallery', [])
            
            print_success(f"Complete sync OK")
            print_success(f"  User: {usuario.get('nombre_completo', 'N/A')}")
            print_success(f"  Schedule: {schedule.get('mes', 'N/A') if schedule else 'None'} {schedule.get('ano', '') if schedule else ''}")
            print_success(f"  Gallery: {len(gallery)} photos")
        else:
            print_error(f"Complete sync failed: {response.status_code}")
            return False
        
        # Test 7: Mass sync
        print_info("\nTesting mass synchronization...")
        response = requests.post(
            f'{base_url}/sincronizar_masiva',
            json=['juan_perez', 'maria_lopez'],
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Mass sync OK - {data.get('total', 0)} users updated")
        else:
            print_error(f"Mass sync failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API server. Is it running?")
        print_info("Start with: python madre_main.py")
        return False
    except Exception as e:
        print_error(f"API test failed: {e}")
        return False

def test_credentials():
    """Test credential storage."""
    print_header("TEST 3: Credential Management")
    
    try:
        from hija_comms import APICommunicator
        
        comm = APICommunicator()
        
        # Test save credentials
        print_info("Testing credential storage...")
        success = comm.save_credentials('test_user', 'test_password')
        if success:
            print_success("Credentials saved successfully")
        else:
            print_error("Failed to save credentials")
            return False
        
        # Test load credentials
        print_info("Testing credential loading...")
        creds = comm.load_credentials()
        if creds and creds.get('username') == 'test_user':
            print_success(f"Credentials loaded OK - User: {creds.get('username')}")
        else:
            print_error("Failed to load credentials")
            return False
        
        # Test password verification
        print_info("Testing password verification...")
        if comm.verify_stored_password('test_password'):
            print_success("Password verification OK")
        else:
            print_error("Password verification failed")
        
        if not comm.verify_stored_password('wrong_password'):
            print_success("Wrong password correctly rejected")
        else:
            print_error("Wrong password not rejected")
        
        # Clean up
        comm.clear_credentials()
        print_info("Test credentials cleaned up")
        
        return True
        
    except Exception as e:
        print_error(f"Credential test failed: {e}")
        return False

def main():
    """Run all tests."""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     SISTEMA GYM v2.0 - SUITE DE PRUEBAS COMPLETA         ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
    
    results = []
    
    # Test 1: Database
    results.append(('Database Operations', test_database()))
    
    # Test 2: API (only if available)
    print_info("\nAPI tests require the server to be running.")
    print_info("If the server is not running, API tests will be skipped.")
    time.sleep(1)
    results.append(('API Server', test_api_server()))
    
    # Test 3: Credentials
    results.append(('Credential Management', test_credentials()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{total}){RESET}")
        print(f"{GREEN}  Sistema funcionando correctamente!{RESET}")
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        print(f"{YELLOW}  Algunos tests fallaron. Revisar mensajes arriba.{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
