import os
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    app.config.update(
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
    )
    mail.init_app(app)


def send_task_created(task):
    recipient = os.getenv("NOTIFICATION_EMAIL")
    if not recipient or not os.getenv("MAIL_USERNAME"):
        return  # Email not configured — silently skip

    reminder_line = ""
    if task.get("reminder_at"):
        reminder_line = f"\nReminder: {task['reminder_at'].strftime('%B %d, %Y at %H:%M')}"
        if task.get("reminder_note"):
            reminder_line += f"\nNote: {task['reminder_note']}"

    description_line = ""
    if task.get("body"):
        description_line = f"\nDescription:\n{task['body']}"

    body = (
        f"New task created in TaskFlow:\n\n"
        f"Title: {task['title']}\n"
        f"Status: Pending"
        f"{reminder_line}"
        f"{description_line}"
    ).strip()

    msg = Message(
        subject=f"[TaskFlow] New task: {task['title']}",
        recipients=[recipient],
        body=body,
    )
    try:
        mail.send(msg)
    except Exception as e:
        # Don't crash the request if email fails
        print(f"[mail] Failed to send email: {e}")
