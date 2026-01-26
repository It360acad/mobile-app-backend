#!/usr/bin/env python
"""
Test script for async OTP email functionality

This script tests the background email sending using Celery tasks
for OTP functionality in the IT360 Academy backend.

Usage:
    python test_async_otp.py

Make sure to:
1. Start the Celery worker: ./start_celery_worker.sh
2. Set USE_CONSOLE_EMAIL=true for testing (optional)
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it360acad_backend.settings')
django.setup()

from notification.tasks import send_otp_email, test_celery_connection
from users.models import User
from authentication.models import OTP


def test_celery_connection_basic():
    """Test basic Celery connection"""
    print("🧪 Testing basic Celery connection...")

    try:
        result = test_celery_connection.delay("Test from async OTP script")
        print(f"✅ Task queued successfully: {result.id}")

        # Wait for result
        task_result = result.get(timeout=10)
        print(f"✅ Task completed: {task_result}")
        return True
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False


def test_otp_email_task():
    """Test OTP email task directly"""
    print("\n📧 Testing OTP email task...")

    test_email = "test@example.com"
    test_otp = "123456"

    try:
        # Test verification OTP
        print(f"Sending verification OTP to {test_email}...")
        result = send_otp_email.delay(test_email, test_otp, 'verification')
        print(f"✅ Verification OTP task queued: {result.id}")

        task_result = result.get(timeout=15)
        print(f"✅ Verification OTP sent: {task_result}")

        # Test password reset OTP
        print(f"\nSending password reset OTP to {test_email}...")
        result = send_otp_email.delay(test_email, test_otp, 'password_reset')
        print(f"✅ Password reset OTP task queued: {result.id}")

        task_result = result.get(timeout=15)
        print(f"✅ Password reset OTP sent: {task_result}")

        return True
    except Exception as e:
        print(f"❌ OTP email task failed: {e}")
        return False


def test_with_real_user():
    """Test with a real user from the database"""
    print("\n👤 Testing with real user...")

    try:
        # Get first user
        user = User.objects.first()
        if not user:
            print("⚠️  No users found in database. Creating test user...")
            user = User.objects.create_user(
                email="testuser@example.com",
                password="testpassword123",
                first_name="Test",
                last_name="User"
            )
            print(f"✅ Created test user: {user.email}")

        print(f"Testing with user: {user.email}")

        # Create an OTP for this user
        otp = OTP.create_otp(user, expiry_minutes=10)
        print(f"✅ Generated OTP: {otp.code}")

        # Send OTP via Celery task
        result = send_otp_email.delay(user.email, otp.code, 'verification')
        print(f"✅ Task queued: {result.id}")

        task_result = result.get(timeout=15)
        print(f"✅ Email sent to real user: {task_result}")

        return True
    except Exception as e:
        print(f"❌ Real user test failed: {e}")
        return False


def performance_test():
    """Test performance - multiple concurrent tasks"""
    print("\n⚡ Performance test - sending multiple OTPs...")

    try:
        start_time = time.time()
        tasks = []

        # Queue multiple tasks
        for i in range(5):
            result = send_otp_email.delay(
                f"test{i}@example.com",
                f"12345{i}",
                'verification'
            )
            tasks.append(result)
            print(f"✅ Queued task {i+1}: {result.id}")

        queue_time = time.time() - start_time
        print(f"⏱️  Time to queue 5 tasks: {queue_time:.2f}s")

        # Wait for all tasks to complete
        print("Waiting for all tasks to complete...")
        results = []
        for i, task in enumerate(tasks):
            try:
                task_result = task.get(timeout=20)
                results.append(task_result)
                print(f"✅ Task {i+1} completed: {task_result}")
            except Exception as e:
                print(f"❌ Task {i+1} failed: {e}")
                results.append(False)

        total_time = time.time() - start_time
        successful = sum(1 for r in results if r is True)

        print(f"\n📊 Performance Results:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Queue time: {queue_time:.2f}s")
        print(f"   Execution time: {total_time - queue_time:.2f}s")
        print(f"   Successful tasks: {successful}/5")
        print(f"   Average time per task: {(total_time - queue_time)/5:.2f}s")

        return successful == 5
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def check_worker_status():
    """Check if Celery worker is running"""
    print("🔍 Checking Celery worker status...")

    try:
        from celery import current_app

        # Check registered tasks
        registered_tasks = list(current_app.tasks.keys())
        notification_tasks = [t for t in registered_tasks if 'notification.tasks' in t]

        print(f"✅ Celery app configured")
        print(f"✅ Total registered tasks: {len(registered_tasks)}")
        print(f"✅ Notification tasks: {len(notification_tasks)}")

        for task in notification_tasks:
            print(f"   - {task}")

        # Try to get worker stats
        try:
            from celery import current_app
            i = current_app.control.inspect()
            stats = i.stats()
            if stats:
                print(f"✅ Active workers: {len(stats)}")
                for worker_name, worker_stats in stats.items():
                    print(f"   - {worker_name}: {worker_stats.get('pool', {}).get('processes', 'unknown')} processes")
            else:
                print("⚠️  No active workers found. Make sure to start the worker:")
                print("   ./start_celery_worker.sh")
                return False
        except Exception as e:
            print(f"⚠️  Could not get worker stats: {e}")
            print("   Worker might not be running. Start with: ./start_celery_worker.sh")
            return False

        return True
    except Exception as e:
        print(f"❌ Celery check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 IT360 Academy - Async OTP Email Test")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check email backend
    from django.conf import settings
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    if hasattr(settings, 'USE_CONSOLE_EMAIL'):
        print(f"Console email: {settings.USE_CONSOLE_EMAIL}")

    print("\n" + "=" * 50)

    tests = [
        ("Worker Status", check_worker_status),
        ("Basic Celery Connection", test_celery_connection_basic),
        ("OTP Email Task", test_otp_email_task),
        ("Real User Test", test_with_real_user),
        ("Performance Test", performance_test),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Async OTP is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start your Django server: python manage.py runserver")
        print("   2. Make sure Celery worker is running: ./start_celery_worker.sh")
        print("   3. Test the /api/auth/resend-otp/ endpoint")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == len(results)


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test script failed: {e}")
        sys.exit(1)
