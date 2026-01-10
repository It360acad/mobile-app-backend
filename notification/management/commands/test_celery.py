"""
Django management command to test Celery connection and task execution.
"""
from django.core.management.base import BaseCommand
from notification.tasks import test_celery_connection
import time


class Command(BaseCommand):
    help = 'Test Celery connection and task execution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Test async task execution (fire and forget)',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Test sync task execution (wait for result)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🧪 Testing Celery Connection...\n'))
        
        # Test 1: Check if Celery app is configured
        try:
            from it360acad_backend.celery import app
            self.stdout.write(self.style.SUCCESS('✅ Celery app imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to import Celery app: {str(e)}'))
            return

        # Test 2: Check Redis connection
        try:
            broker_url = app.conf.broker_url
            self.stdout.write(self.style.SUCCESS(f'✅ Broker URL: {broker_url}'))
            
            # Try to connect
            with app.connection() as conn:
                conn.ensure_connection(max_retries=3)
            self.stdout.write(self.style.SUCCESS('✅ Redis connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Redis connection failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('\n💡 Make sure:'))
            self.stdout.write(self.style.WARNING('   1. Redis/Upstash is running and accessible'))
            self.stdout.write(self.style.WARNING('   2. CELERY_BROKER_URL is set correctly in .env'))
            self.stdout.write(self.style.WARNING('   3. Celery worker is running: celery -A it360acad_backend worker --loglevel=info'))
            return

        # Test 3: Execute task
        if options['sync']:
            self.stdout.write(self.style.WARNING('\n📤 Testing SYNC task execution (waiting for result)...'))
            try:
                result = test_celery_connection.apply(args=("Sync test from management command",))
                self.stdout.write(self.style.SUCCESS(f'✅ Task executed successfully!'))
                self.stdout.write(self.style.SUCCESS(f'   Result: {result.result}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Task execution failed: {str(e)}'))
        else:
            # Default: async execution
            self.stdout.write(self.style.WARNING('\n📤 Testing ASYNC task execution (fire and forget)...'))
            try:
                task = test_celery_connection.delay("Async test from management command")
                self.stdout.write(self.style.SUCCESS(f'✅ Task queued successfully!'))
                self.stdout.write(self.style.SUCCESS(f'   Task ID: {task.id}'))
                self.stdout.write(self.style.WARNING('\n⏳ Waiting 3 seconds for task to complete...'))
                time.sleep(3)
                
                # Check task status
                if task.ready():
                    if task.successful():
                        self.stdout.write(self.style.SUCCESS(f'✅ Task completed successfully!'))
                        self.stdout.write(self.style.SUCCESS(f'   Result: {task.result}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Task failed: {task.info}'))
                else:
                    self.stdout.write(self.style.WARNING('⏳ Task is still processing...'))
                    self.stdout.write(self.style.WARNING('   Check Celery worker logs to see the result'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to queue task: {str(e)}'))
                self.stdout.write(self.style.WARNING('\n💡 Make sure Celery worker is running:'))
                self.stdout.write(self.style.WARNING('   celery -A it360acad_backend worker --loglevel=info'))

        self.stdout.write(self.style.SUCCESS('\n✨ Test completed!\n'))

