import os
import random
import hashlib
import discord
from discord.ext import commands

# --- الإعدادات العامة ---
SECRET_SALT = "EARTH_SUPER_SECRET_2026"
ALLOWED_ROLE_ID = 0  # ضع ID الرتبة المسموح لها بتوليد المفاتيح (أو 0 للجميع)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- قواعد البيانات الموقتة (في الذاكرة) ---
# يمكنك استبدالها بملف JSON أو قاعدة بيانات SQLite لاحقاً لحفظ البيانات عند إعادة تشغيل البوت
generated_keys = set()      # جميع الأكواد الموالدة لمنع التكرار
used_keys = set()           # الأكواد التي تم استخدامها
active_users = set()        # قائمة ID المستخدمين الذين فعّلوا كوداً

def generate_earth_key() -> str:
    """توليد كود فريد وغير مكرر مع مطابقة التوقيع الرقمي."""
    while True:
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        base = "".join(random.choices(chars, k=6))
        raw_data = base + SECRET_SALT
        full_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest().upper()
        checksum = full_hash[:4]
        key = f"EARTH-{base}-{checksum}"
        
        # التأكد من عدم تكرار الكود نهائياً
        if key not in generated_keys:
            generated_keys.add(key)
            return key

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح باسم البوت: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="!help_earth | نظام التفعيل"))

# --- 1. أمر قائمة الأوامر والإحصائيات الشاملة ---
@bot.command(name="help_earth", aliases=["earth_help", "stats", "status"])
async def show_help_and_stats(ctx):
    """عرض قائمة الأوامر وإحصائيات نظام الأكواد والمستخدمين."""
    total_generated = len(generated_keys)
    total_used = len(used_keys)
    available_keys = total_generated - total_used
    total_users = len(active_users)

    embed = discord.Embed(
        title="🤖 لوحة تحكم وإحصائيات بوت Earth",
        description="جميع الأوامر والإحصائيات المتاحة بالنظام:",
        color=discord.Color.green()
    )

    # قسم الأوامر
    embed.add_field(
        name="📜 الأوامر المتاحة",
        value=(
            "• `!key <count>` أو `!genkey`: توليد أكواد تفعيل جديدة (مثال: `!key 5`).\n"
            "• `!redeem <code>` أو `!use`: استخدام وتفعيل كود خاص بك.\n"
            "• `!stats` أو `!help_earth`: عرض هذه القائمة والإحصائيات."
        ),
        inline=False
    )

    # قسم الإحصائيات
    embed.add_field(
        name="📊 الإحصائيات الحالية",
        value=(
            f"• **إجمالي الأكواد المنشأة:** `{total_generated}`\n"
            f"• **الأكواد المستعملة:** `{total_used}`\n"
            f"• **الأكواد المتاحة للتفعيل:** `{available_keys}`\n"
            f"• **إجمالي المستخدمين الفعّالين:** `{total_users}`"
        ),
        inline=False
    )

    embed.set_footer(text="جميع الحقوق محفوظة © 2026 - Earth Server")
    await ctx.send(embed=embed)

# --- 2. أمر توليد الأكواد ---
@bot.command(name="key", aliases=["genkey", "k"])
async def gen_key(ctx, count: int = 1):
    """توليد عدد محدد من المفاتيح المضمونة عدم التكرار."""
    # التحقق من الرتبة إذا كانت مفعّلة
    if ALLOWED_ROLE_ID != 0:
        role = ctx.guild.get_role(ALLOWED_ROLE_ID) if ctx.guild else None
        if role and role not in ctx.author.roles:
            await ctx.send("❌ ليس لديك الصلاحية لتوليد المفاتيح.")
            return

    if count < 1 or count > 50:
        await ctx.send("❌ يرجى إدخال عدد أكواد بين 1 و 50 فقط.")
        return

    new_keys = [generate_earth_key() for _ in range(count)]
    formatted_keys = "\n".join([f"`{k}`" for k in new_keys])

    embed = discord.Embed(
        title="🔑 أكواد تفعيل أداة Earth الجديدة",
        description=f"تم توليد **{count}** كود/أكواد بنجاح (غير مكررة):\n\n{formatted_keys}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="جميع الحقوق محفوظة © 2026 - Earth Server")

    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ تم إرسال {count} كود إلى الخاصة بك يا {ctx.author.mention}!")
    except discord.Forbidden:
        await ctx.send(embed=embed)

# --- 3. أمر تفعيل الكود واستخدامه ---
@bot.command(name="redeem", aliases=["use", "activate"])
async def redeem_key(ctx, key: str = None):
    """تفعيل كود وتحديد الكود كمُستخدَم وتجسيل المستخدم."""
    if not key:
        await ctx.send("❌ يرجى إدخال الكود مع الأمر! مثال: `!redeem EARTH-XXXXXX-XXXX`")
        return

    clean_key = key.strip().upper()

    if clean_key in used_keys:
        await ctx.send("❌ هذا الكود تم استخدامه من قبل!")
        return

    if clean_key not in generated_keys:
        await ctx.send("❌ هذا الكود غير صحيح أو لم يتم توليده عبر النظام!")
        return

    # علم الكود كمستعمل وسجل المستخدم
    used_keys.add(clean_key)
    active_users.add(ctx.author.id)

    embed = discord.Embed(
        title="🎉 تم التفعيل بنجاح!",
        description=f"مرحباً بك {ctx.author.mention}، تم تفعيل كودك `{clean_key}` بنجاح وحسابك أصبح مسجلاً.",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# تشغيل البوت عبر توكن Railway
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
