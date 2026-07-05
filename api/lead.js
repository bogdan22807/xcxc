// Vercel serverless function: forwards website leads to a Telegram bot.
// Configure these Environment Variables in the Vercel dashboard:
//   TELEGRAM_BOT_TOKEN  — token from @BotFather
//   TELEGRAM_CHAT_ID    — your chat/user id (or group/channel id)

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!token || !chatId) {
    return res.status(500).json({ error: "Server is not configured" });
  }

  const body = typeof req.body === "string" ? safeParse(req.body) : req.body || {};
  const { siteType, budget, wishes, name, phone, email } = body;

  if (!name || !phone || !email) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const text = [
    "🆕 <b>Нова заявка з сайту XTRA</b>",
    "",
    `👤 Ім'я: ${esc(name)}`,
    `📞 Телефон: ${esc(phone)}`,
    `✉️ Email: ${esc(email)}`,
    `🌐 Тип сайту: ${esc(siteType) || "—"}`,
    `💰 Бюджет: ${esc(budget) || "—"}`,
    `📝 Побажання: ${esc(wishes) || "—"}`,
  ].join("\n");

  try {
    const tgRes = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "HTML",
        disable_web_page_preview: true,
      }),
    });

    if (!tgRes.ok) {
      const detail = await tgRes.text();
      return res.status(502).json({ error: "Telegram rejected the message", detail });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    return res.status(500).json({ error: "Failed to send" });
  }
}

function esc(value) {
  if (!value) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function safeParse(str) {
  try {
    return JSON.parse(str);
  } catch {
    return {};
  }
}
