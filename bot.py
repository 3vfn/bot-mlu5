import os
import random
import hashlib
import discord
from discord.ext import commands

# الإعدادات الموحدة للربط
SECRET_SALT = "EARTH_SUPER_SECRET_2026"
ALLOWED_ROLE_ID = 123456789012345678  # ضع هنا ID الرتبة المسموح لها بتوليد المفاتيح (أو اتركه 0 للجميع)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def generate_earth_key() -> str:
    """توليد كود تفعيل موحد مع مطابقة التوقيع الرقمي."""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    base = "".join(random.choices(chars, k=6))
    raw_data = base + SECRET_SALT
    full_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest().upper()
    checksum = full_hash[:4]
    return f"EARTH-{base}-{checksum}"

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح باسم البوت: {bot.user.name}")

@bot.command(name="key", aliases=["genkey", "k"])
async def gen_key(ctx, count: int = 1):
    """أمر توليد أكواد التفعيل إما عبر الخاص أو في القناة."""
    if count < 1 or count > 20:
        await ctx.send("❌ يرجى إدخال عدد أكواد بين 1 و 20 فقط.")
        return

    keys = [generate_earth_key() for _ in range(count)]
    formatted_keys = "\n".join([f"`{k}`" for k in keys])

    embed = discord.Embed(
        title="🔑 أكواد تفعيل أداة Earth",
        description=f"تم توليد **{count}** كود/أكواد بنجاح:\n\n{formatted_keys}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="جميع الحقوق محفوظة © 2026 - Earth Server")

    try:
        # إرسال المفاتيح على الخاص لضمان الخصوصية
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ تم إرسال الأكواد إلى الخاص يا {ctx.author.mention}!")
    except discord.Forbidden:
        await ctx.send(embed=embed)

# تشغيل البوت باستخدام التوكن المعرف في Railway
bot.run(os.getenv("DISCORD_TOKEN"))
