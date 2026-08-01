import os
import random
import hashlib
import discord
from discord.ext import commands

# 🔑 المفتاح السري الموحد لتشفير الأكواد
SECRET_SALT = "EARTH_SUPER_SECRET_2026"

# ضع ID الرتبة المسموح لها بتوليد المفاتيح (أو اتركه 0 للسماح للجميع)
ALLOWED_ROLE_ID = 0 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- قاعدة بيانات الأكواد والبصمات ---
# Structure: key -> {"used": True/False, "hwid": "XYZ...", "user_id": 123456}
keys_db = {}

def generate_earth_key() -> str:
    """توليد كود فريد وغير مكرر مع مطابقة التوقيع الرقمي."""
    while True:
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        base = "".join(random.choices(chars, k=6))
        raw_data = base + SECRET_SALT
        full_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest().upper()
        checksum = full_hash[:4]
        key = f"EARTH-{base}-{checksum}"
        
        if key not in keys_db:
            keys_db[key] = {"used": False, "hwid": None, "user_id": None}
            return key

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"✅ تم تشغيل بوت Earth بنجاح باسم: {bot.user.name}")
    print(f"🔒 نظام الحماية وتقييد HWID نشط ومفعل.")
    print(f"==================================================")
    await bot.change_presence(activity=discord.Game(name="!key | Earth Spoofer System"))

@bot.command(name="key", aliases=["genkey", "k"])
async def gen_key(ctx, count: int = 1):
    """أمر توليد أكواد جديدة لـ Earth Spoofer"""
    if ALLOWED_ROLE_ID != 0:
        role = ctx.guild.get_role(ALLOWED_ROLE_ID) if ctx.guild else None
        if role and role not in ctx.author.roles:
            await ctx.send("❌ ليس لديك الصلاحية لتوليد مفاتيح التفعيل.")
            return

    if count < 1 or count > 50:
        await ctx.send("❌ يرجى إدخال عدد أكواد بين 1 و 50 فقط.")
        return

    new_keys = [generate_earth_key() for _ in range(count)]
    formatted_keys = "\n".join([f"`{k}`" for k in new_keys])

    embed = discord.Embed(
        title="🔑 أكواد تفعيل أداة Earth Spoofer",
        description=f"تم توليد **{count}** كود بنجاح (ملاحظة: الكود يعمل على **جهاز واحد فقط** عند التفعيل):\n\n{formatted_keys}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="جميع الحقوق محفوظة © 2026 - Earth Spoofer")

    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ تم إرسال الأكواد إلى الخاص يا {ctx.author.mention}!")
    except discord.Forbidden:
        await ctx.send(embed=embed)

@bot.command(name="reset_hwid")
async def reset_hwid(ctx, key: str):
    """أمر إعادة ضبط الـ HWID لكود معين في حال قام العميل بتغيير جهازه"""
    clean_key = key.strip().upper()
    if clean_key in keys_db:
        keys_db[clean_key]["used"] = False
        keys_db[clean_key]["hwid"] = None
        await ctx.send(f"✅ تم فك ربط الكود `{clean_key}` بنجاح. يمكن استخدامه على جهاز جديد الآن.")
    else:
        await ctx.send("❌ الكود غير موجود في قاعدة البيانات.")

# تشغيل البوت عبر التوكين
TOKEN = os.getenv("DISCORD_TOKEN") or "ضع_توكين_البوت_هنا"
if __name__ == "__main__":
    bot.run(TOKEN)
