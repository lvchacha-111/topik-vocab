# -*- coding: utf-8 -*-
"""每天生成单词邮件并发送到 QQ 邮箱。由 GitHub Actions 定时触发。"""

import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


START_DATE = datetime.date(2026, 9, 2)


def load_data():
    with open("data/daily.json", encoding="utf-8") as f:
        days = json.load(f)
    with open("data/phrases.json", encoding="utf-8") as f:
        phrases = json.load(f)
    return days, phrases


def today_day_num():
    return (datetime.date.today() - START_DATE).days + 1


def pick_day(days, day_num):
    # 精确匹配当天；没有就用最接近的一档（由易到难）
    exact = next((d for d in days if d["day"] == day_num), None)
    if exact:
        return exact
    prev = [d for d in days if d["day"] <= day_num]
    return prev[-1] if prev else days[0]


def build_html(day, phrase):
    rows = "\n".join(
        f"""
        <tr>
          <td style="padding:14px 0;border-bottom:1px solid #fbe4ec;">
            <strong style="color:#4a3540;font-size:18px;">{w['kr']}</strong>
            <span style="color:#c68aa0;">[{w['roman']}]</span>
            <span style="display:inline-block;margin-left:8px;background:#f7d3e0;color:#d4538b;font-size:11px;padding:2px 8px;border-radius:4px;">{w['pos']}</span>
            <span style="color:#7a5f6c;margin-left:8px;">{w['meaning']}</span>
            <div style="color:#c68aa0;font-size:13px;margin-top:6px;">{w['example']}</div>
            <div style="color:#d3b5c2;font-size:13px;">{w['cn']}</div>
          </td>
        </tr>"""
        for w in day["words"]
    )
    return f"""
    <div style="max-width:600px;margin:0 auto;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;">
      <div style="background:linear-gradient(135deg,#fbd3e0,#f09dc0);padding:32px;text-align:center;color:#fff;border-radius:16px 16px 0 0;">
        <div style="font-size:12px;letter-spacing:3px;opacity:.8;">TOPIK 4级</div>
        <div style="font-size:26px;font-weight:700;margin-top:8px;">Sam · Chase 的韩语计划</div>
        <div style="font-size:13px;margin-top:8px;opacity:.85;">第 {day['day']} 天 · {day['level']} · {day['label']}</div>
      </div>
      <div style="background:#fff;padding:24px 32px;border-radius:0 0 16px 16px;border:1px solid #fbe4ec;">
        <table style="width:100%;border-collapse:collapse;">{rows}</table>
        <div style="margin-top:24px;padding-top:20px;border-top:1px solid #fbe4ec;text-align:center;">
          <div style="font-size:18px;color:#d4538b;font-weight:700;">{phrase['kr']}</div>
          <div style="font-size:12px;color:#c68aa0;margin-top:6px;">今天请对 ta 说 · {phrase['cn']}</div>
        </div>
      </div>
    </div>"""


def send_email(html, subject):
    sender = os.environ["QQ_EMAIL"]
    receiver = os.environ.get("QQ_RECEIVER", sender)
    auth_code = os.environ["QQ_SMTP_CODE"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(html, "html", "utf-8"))

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, auth_code)
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()


def main():
    days, phrases = load_data()
    day_num = today_day_num()
    day = pick_day(days, day_num)
    phrase = phrases[(day_num - 1) % len(phrases)]
    html = build_html(day, phrase)
    send_email(html, f"Sam和Chase的韩语计划 · 第{day['day']}天单词")
    print(f"sent day {day['day']} ({len(day['words'])} words)")


if __name__ == "__main__":
    main()
