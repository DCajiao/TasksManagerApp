import os
from flask_mail import Mail, Message

mail = Mail()

LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "assets", "img", "logo_raw.png")


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


def _build_html(task):
    reminder_block = ""
    if task.get("reminder_at"):
        note_row = ""
        if task.get("reminder_note"):
            note_row = f"""
            <tr>
              <td style="padding:4px 0 0 0; color:#94a3b8; font-size:13px;">
                {task['reminder_note']}
              </td>
            </tr>"""
        reminder_block = f"""
        <tr>
          <td style="padding:24px 0 0 0;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background:#1e1b4b; border:1px solid rgba(99,102,241,.3); border-radius:8px;">
              <tr>
                <td style="padding:14px 16px;">
                  <p style="margin:0 0 4px 0; font-size:11px; font-weight:600; letter-spacing:.08em;
                             text-transform:uppercase; color:#6366f1;">Reminder</p>
                  <p style="margin:0; font-size:14px; font-weight:600; color:#a5b4fc;">
                    🔔 {task['reminder_at'].strftime('%B %d, %Y at %H:%M')}
                  </p>{note_row}
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    description_block = ""
    if task.get("body"):
        description_block = f"""
        <tr>
          <td style="padding:20px 0 0 0;">
            <p style="margin:0 0 6px 0; font-size:11px; font-weight:600; letter-spacing:.08em;
                       text-transform:uppercase; color:#475569;">Description</p>
            <p style="margin:0; font-size:14px; line-height:1.6; color:#94a3b8;
                       white-space:pre-wrap;">{task['body']}</p>
          </td>
        </tr>"""

    ai_block = ""
    if task.get("ai_recommendation"):
        ai_block = f"""
        <tr>
          <td style="padding:20px 0 0 0;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background:rgba(99,102,241,.08); border:1px solid rgba(99,102,241,.2); border-radius:8px;">
              <tr>
                <td style="padding:14px 16px;">
                  <p style="margin:0 0 6px 0; font-size:11px; font-weight:600; letter-spacing:.08em;
                             text-transform:uppercase; color:#6366f1;">✨ AI Recommendation</p>
                  <p style="margin:0; font-size:14px; line-height:1.6; color:#a5b4fc;">
                    {task['ai_recommendation']}
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    logo_tag = '<img src="cid:logo" alt="TaskFlow" width="28" height="28" style="border-radius:6px; vertical-align:middle; margin-right:8px;">'
    if not os.path.exists(LOGO_PATH):
        logo_tag = '<span style="display:inline-block;width:28px;height:28px;background:#6366f1;border-radius:6px;vertical-align:middle;margin-right:8px;"></span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#0f1117;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#1a1d27;border-radius:12px 12px 0 0;padding:24px 32px;
                       border-bottom:1px solid rgba(99,102,241,.2);">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    {logo_tag}
                    <span style="font-size:18px;font-weight:700;color:#f1f5f9;vertical-align:middle;">TaskFlow</span>
                  </td>
                  <td align="right">
                    <span style="font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#475569;">
                      New Task
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#1a1d27;padding:32px 32px 0 32px;border-radius:0;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">

                <!-- Title -->
                <tr>
                  <td>
                    <p style="margin:0 0 8px 0;font-size:11px;font-weight:600;letter-spacing:.08em;
                               text-transform:uppercase;color:#475569;">Task</p>
                    <h1 style="margin:0;font-size:22px;font-weight:700;color:#f1f5f9;line-height:1.3;">
                      {task['title']}
                    </h1>
                  </td>
                </tr>

                <!-- Status -->
                <tr>
                  <td style="padding:16px 0 0 0;">
                    <span style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;
                                 border-radius:99px;font-size:12px;font-weight:600;
                                 background:rgba(100,116,139,.12);color:#94a3b8;
                                 border:1px solid rgba(100,116,139,.25);">
                      ○ &nbsp;Pending
                    </span>
                  </td>
                </tr>

                {description_block}
                {ai_block}
                {reminder_block}

                <!-- Divider -->
                <tr>
                  <td style="padding:28px 0 0 0;">
                    <hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:0;">
                  </td>
                </tr>

                <!-- Created at -->
                <tr>
                  <td style="padding:16px 0 0 0;">
                    <p style="margin:0;font-size:12px;color:#334155;">
                      Created on
                      <strong style="color:#475569;">
                        {task['created_at'].strftime('%B %d, %Y at %H:%M') if task.get('created_at') else ''}
                      </strong>
                    </p>
                  </td>
                </tr>

              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#1a1d27;border-radius:0 0 12px 12px;padding:20px 32px 28px 32px;
                       border-top:1px solid rgba(255,255,255,.04);">
              <p style="margin:0;font-size:12px;color:#334155;text-align:center;">
                You're receiving this because you're subscribed to TaskFlow notifications.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _build_plaintext(task):
    lines = [
        "New task created in TaskFlow",
        "─" * 36,
        f"Title:  {task['title']}",
        "Status: Pending",
    ]
    if task.get("reminder_at"):
        lines.append(f"Reminder: {task['reminder_at'].strftime('%B %d, %Y at %H:%M')}")
        if task.get("reminder_note"):
            lines.append(f"Note: {task['reminder_note']}")
    if task.get("body"):
        lines += ["", "Description:", task["body"]]
    if task.get("ai_recommendation"):
        lines += ["", "✨ AI Recommendation:", task["ai_recommendation"]]
    if task.get("created_at"):
        lines += ["", f"Created: {task['created_at'].strftime('%B %d, %Y at %H:%M')}"]
    return "\n".join(lines)


def send_task_created(task):
    if not os.getenv("MAIL_USERNAME"):
        return

    from src.db import get_db
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT email FROM subscribers WHERE active = TRUE")
        rows = cur.fetchall()

    recipients = [row["email"] for row in rows]
    if not recipients:
        return

    msg = Message(
        subject=f"[TaskFlow] New task: {task['title']}",
        recipients=recipients,
        body=_build_plaintext(task),
        html=_build_html(task),
    )

    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            msg.attach(
                filename="logo.png",
                content_type="image/png",
                data=f.read(),
                disposition="inline",
                headers={"Content-ID": "<logo>"},
            )

    try:
        mail.send(msg)
    except Exception as e:
        print(f"[mail] Failed to send email: {e}")
