import aiosqlite
from config import DB_FILE


async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            asin TEXT PRIMARY KEY,
            last_known_price REAL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tracked_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asin TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (asin) REFERENCES products(asin),
            UNIQUE(user_id, asin)
        )
        """)
        await db.commit()

async def add_user(telegram_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
        await db.commit()

async def get_user_id(telegram_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def add_product(telegram_id, asin, last_known_price=None):
    await add_user(telegram_id)
    user_id = await get_user_id(telegram_id)
    async with aiosqlite.connect(DB_FILE) as db:
        # Ensure product exists in products table
        await db.execute(
            "INSERT OR IGNORE INTO products (asin, last_known_price) VALUES (?, ?)",
            (asin, last_known_price)
        )
        # Add tracked product
        await db.execute(
            "INSERT OR IGNORE INTO tracked_products (user_id, asin) VALUES (?, ?)",
            (user_id, asin)
        )
        await db.commit()

async def check_asin(asin):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT 1 FROM products WHERE asin = ?", (asin,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def get_all_tracked():
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("""
        SELECT users.telegram_id, tracked_products.asin, products.last_known_price
        FROM tracked_products
        JOIN users ON tracked_products.user_id = users.id
        JOIN products ON tracked_products.asin = products.asin
        """) as cursor:
            return await cursor.fetchall()

async def update_price(asin, new_price):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE products SET last_known_price = ? WHERE asin = ?",
            (new_price, asin)
        )
        await db.commit()

async def get_user_products(telegram_id):
    async with aiosqlite.connect(DB_FILE) as db:
        user_id = await get_user_id(telegram_id)
        if user_id is None:
            return []
        async with db.execute("SELECT asin FROM tracked_products WHERE user_id = ?", (user_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def remove_product(telegram_id, asin):
    async with aiosqlite.connect(DB_FILE) as db:
        user_id = await get_user_id(telegram_id)
        if user_id is None:
            return
        await db.execute("DELETE FROM tracked_products WHERE asin = ? AND user_id = ?", (asin, user_id))
        await db.commit()

async def get_telegram_id(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT telegram_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def remove_user(telegram_id):
    async with aiosqlite.connect(DB_FILE) as db:
        user_id = await get_user_id(telegram_id)
        if user_id is None:
            return
        await db.execute("DELETE FROM tracked_products WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()

async def get_product_price(asin):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT last_known_price FROM products WHERE asin = ?", (asin,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


if __name__ == "__main__":
    import asyncio
    from config import DB_FILE

    async def main():
        await init_db()
        print("Database initialized.")

    asyncio.run(main())