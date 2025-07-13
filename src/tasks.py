import asyncio
async def send_email_notification(recipient: str, subject: str, body: str):
    await asyncio.sleep(5)  # Simulate network delay
    print(f"Email sent to {recipient}: {subject} - {body}")
