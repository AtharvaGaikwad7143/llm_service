from app.tasks import test_task

result = test_task.delay(
    "Hello from Celery"
)

print("Task ID:", result.id)
print("Task submitted successfully.")