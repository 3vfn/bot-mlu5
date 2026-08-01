import os
import random
import hashlib
import discord
from discord.ext import commands

# إعداد المتغيرات السرية
SECRET_SALT = "MLU5AYH_SUPER_SECRET_2026"

def generate_key():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    base = "".join(random.choices(chars, k=6))
    raw_data = base + SECRET_SALT
    full_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest().upper()
    checksum = full_hash[:4]
    return f"MLU-{base}-{checksum}"

# إعداد البوت مع الصلاحيات المناسبة
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")

@bot.command(name="generate", help="توليد أكواد جديدة. الاستخدام: !generate [العدد]")
async def generate_keys(ctx, count: int = 5):
    # التحقق من أن العدد ضمن نطاق مقبول
    if count <= 0 or count > 50:
        await ctx.send("❌ الرجاء إدخال رقم صحيح بين 1 و 50.")
        return

    keys_list = [generate_key() for _ in range(count)]
    result_text = "\n".join(keys_list)

    # إرسال الأكواد في رسالة خاصة (DM) أو في الشات
    embed = discord.Embed(
        title="🔑 مولد أكواد Mlu",
        description=f"تم توليد الأكواد بنجاح:\n```text\n{result_text}\n```",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"بواسطة: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

# تشغيل البوت باستخدام التوكن من متغيرات البيئة
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ خطأ: لم يتم العثور على توكن البوت في متغيرات البيئة (DISCORD_TOKEN)")
