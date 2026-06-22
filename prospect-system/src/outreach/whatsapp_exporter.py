"""
Exports WhatsApp message drafts as a clickable HTML page.

Each approved draft becomes a row with:
  - Business name, city, phone
  - "Abrir en WhatsApp" button → wa.me link with pre-filled message
  - "Marcar enviado" button (marks the draft as sent in the DB)

Usage: run.bat whatsapp export  →  opens data/whatsapp_links.html in the browser
"""
from __future__ import annotations

import csv
import html as html_lib
from datetime import datetime
from pathlib import Path

from loguru import logger


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WhatsApp Outreach — GestiCitas ({count} leads)</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #f0f2f5; margin: 0; padding: 1rem; }}
    h1 {{ color: #128c7e; margin-bottom: 0.25rem; }}
    p.sub {{ color: #555; margin-top: 0; font-size: 0.9rem; }}
    table {{ border-collapse: collapse; width: 100%; background: white;
             border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
    th {{ background: #128c7e; color: white; padding: .75rem 1rem; text-align: left; font-size: .85rem; }}
    td {{ padding: .65rem 1rem; border-bottom: 1px solid #eee; vertical-align: middle; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f9fafb; }}
    .name {{ font-weight: 600; }}
    .city {{ color: #666; font-size: .85rem; }}
    .phone {{ font-family: monospace; font-size: .9rem; }}
    .btn {{ display: inline-block; padding: .45rem .9rem; border-radius: 20px;
            font-size: .85rem; text-decoration: none; font-weight: 600; }}
    .btn-wa {{ background: #25d366; color: white; }}
    .btn-wa:hover {{ background: #1ebe5d; }}
    .btn-sent {{ background: #e8f5e9; color: #388e3c; cursor: default; }}
    .sent-label {{ color: #388e3c; font-size: .8rem; }}
    .preview {{ font-size: .78rem; color: #888; white-space: pre-wrap;
                max-height: 80px; overflow: hidden; }}
    .stats {{ background: white; border-radius: 10px; padding: 1rem 1.5rem;
              margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,.1);
              display: flex; gap: 2rem; }}
    .stat {{ text-align: center; }}
    .stat-n {{ font-size: 2rem; font-weight: 700; color: #128c7e; }}
    .stat-l {{ font-size: .8rem; color: #666; }}
  </style>
</head>
<body>
  <h1>📱 WhatsApp Outreach — GestiCitas</h1>
  <p class="sub">Generado el {date} · {count} mensajes listos para enviar</p>

  <div class="stats">
    <div class="stat"><div class="stat-n">{count}</div><div class="stat-l">Mensajes</div></div>
    <div class="stat"><div class="stat-n">{sent}</div><div class="stat-l">Ya enviados</div></div>
    <div class="stat"><div class="stat-n">{pending}</div><div class="stat-l">Pendientes</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Negocio</th>
        <th>Teléfono</th>
        <th>Mensaje (preview)</th>
        <th>Acción</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <p style="color:#999; font-size:.75rem; margin-top:1rem;">
    Haz clic en "Abrir en WhatsApp" para enviar el mensaje desde tu teléfono o WhatsApp Web.
    El texto ya viene escrito — solo tienes que pulsar Enviar.
  </p>
</body>
</html>
"""

_ROW_TEMPLATE = """\
      <tr>
        <td>{idx}</td>
        <td>
          <div class="name">{name}</div>
          <div class="city">{city}</div>
        </td>
        <td class="phone">{phone}</td>
        <td><div class="preview">{preview}</div></td>
        <td>
          <a class="btn btn-wa" href="{wa_link}" target="_blank">💬 Abrir en WhatsApp</a>
        </td>
      </tr>"""

_ROW_SENT_TEMPLATE = """\
      <tr style="opacity:.55">
        <td>{idx}</td>
        <td>
          <div class="name">{name}</div>
          <div class="city">{city}</div>
        </td>
        <td class="phone">{phone}</td>
        <td><div class="preview">{preview}</div></td>
        <td><span class="sent-label">✅ Enviado</span></td>
      </tr>"""


def export_whatsapp_html(drafts_with_leads: list[dict], output_path: str) -> int:
    """
    Render an HTML file with wa.me links for each draft.
    Returns the number of leads exported.
    """
    rows_html = []
    sent_count = 0

    for idx, item in enumerate(drafts_with_leads, 1):
        draft = item["draft"]
        lead = item["lead"]
        is_sent = draft.whatsapp_status == "sent"

        name = html_lib.escape(lead.name or "")
        city_str = html_lib.escape(f"{lead.city or ''} ({lead.province or ''})".strip(" ()"))
        phone = html_lib.escape(draft.phone or "")
        preview = html_lib.escape(draft.message_text[:200] if draft.message_text else "")
        wa_link = html_lib.escape(draft.wa_link or "")

        if is_sent:
            sent_count += 1
            rows_html.append(_ROW_SENT_TEMPLATE.format(
                idx=idx, name=name, city=city_str, phone=phone, preview=preview,
            ))
        else:
            rows_html.append(_ROW_TEMPLATE.format(
                idx=idx, name=name, city=city_str, phone=phone,
                preview=preview, wa_link=wa_link,
            ))

    total = len(drafts_with_leads)
    html_content = _HTML_TEMPLATE.format(
        count=total,
        sent=sent_count,
        pending=total - sent_count,
        date=datetime.now().strftime("%d/%m/%Y %H:%M"),
        rows="\n".join(rows_html),
    )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    logger.success(f"[WhatsApp] HTML exportado → {output}")
    return total


def export_whatsapp_csv(drafts_with_leads: list[dict], output_path: str) -> int:
    """Export wa.me links as CSV (name, phone, wa_link, message_text)."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nombre", "telefono", "ciudad", "provincia", "wa_link", "mensaje"])
        for item in drafts_with_leads:
            d = item["draft"]
            l = item["lead"]
            writer.writerow([
                l.name or "",
                d.phone or "",
                l.city or "",
                l.province or "",
                d.wa_link or "",
                (d.message_text or "").replace("\n", " "),
            ])

    logger.success(f"[WhatsApp] CSV exportado → {output}")
    return len(drafts_with_leads)
