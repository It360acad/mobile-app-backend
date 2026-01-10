#!/usr/bin/env python
"""
Quick Celery test script - Run this to test if Celery is working.

Usage:
    python test_celery_quick.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it360acad_backend.settings')
django.setup()

from notification.tasks import test_celery_connection
import time

def main():
    print("\n" + "="*60)
    print("🧪 CELERY QUICK TEST")
    print("="*60 + "\n")
    
    # Test 1: Import check
    print("1️⃣  Testing Celery app import...")
    try:
        from it360acad_backend.celery import app
        print("   ✅ Celery app imported successfully")
        print(f"   📍 Broker URL: {app.conf.broker_url}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        return False
    
    # Test 2: Connection check
    print("\n2️⃣  Testing Redis/Upstash connection...")
    try:
        with app.connection() as conn:
            conn.ensure_connection(max_retries=3)
        print("   ✅ Connection successful!")
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("\n   💡 Troubleshooting:")
        print("      - Check CELERY_BROKER_URL in .env file")
        print("      - Make sure Upstash Redis is accessible")
        print("      - Verify connection string format")
        return False
    
    # Test 3: Task execution
    print("\n3️⃣  Testing task execution...")
    print("   📤 Queuing test task...")
    try:
        task = test_celery_connection.delay("Quick test from script")
        print(f"   ✅ Task queued! ID: {task.id}")
        print("   ⏳ Waiting for worker to process (5 seconds)...")
        
        # Wait for task
        for i in range(5):
            time.sleep(1)
            if task.ready():
                break
            print(f"      ... {i+1}/5")
        
        if task.ready():
            if task.successful():
                print(f"   ✅ Task completed successfully!")
                print(f"   📋 Result: {task.result}")
                print("\n" + "="*60)
                print("🎉 ALL TESTS PASSED! Celery is working correctly!")
                print("="*60 + "\n")
                return True
            else:
                print(f"   ❌ Task failed: {task.info}")
                return False
        else:
            print("   ⚠️  Task is still processing...")
            print("   💡 Make sure Celery worker is running:")
            print("      celery -A it360acad_backend worker --loglevel=info")
            return False
            
    except Exception as e:
        print(f"   ❌ Task execution failed: {str(e)}")
        print("\n   💡 Make sure Celery worker is running:")
        print("      celery -A it360acad_backend worker --loglevel=info")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

