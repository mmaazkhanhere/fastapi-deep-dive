import asyncio
async def send_email_notification(recipient: str, subject: str, body: str):
    await asyncio.sleep(5)  # Simulate network delay
    print(f"Email sent to {recipient}: {subject} - {body}")

async def log_resource_view(resource_id: int, user_id: int):
    await asyncio.sleep(5)  # Simulate network delay
    print(f"Logging view for resource {resource_id} by user {user_id}")