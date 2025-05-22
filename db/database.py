import aiosqlite

DB_FILE = "data.db"
class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    async def init_db(self):
        async with aiosqlite.connect(self.db_file) as db:
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
                last_known_price REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """)
            await db.commit()

    async def add_user(self, telegram_id):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
            await db.commit()

    async def get_user_id(self, telegram_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def add_product(self, telegram_id, asin):
        await self.add_user(telegram_id)
        user_id = await self.get_user_id(telegram_id)
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO tracked_products (user_id, asin) VALUES (?, ?)", (user_id, asin))
            await db.commit()

    async def get_all_tracked(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("""
            SELECT users.telegram_id, tracked_products.asin, tracked_products.last_known_price
            FROM tracked_products
            JOIN users ON tracked_products.user_id = users.id
            """) as cursor:
                return await cursor.fetchall()

    async def update_price(self, telegram_id, asin, new_price):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
            UPDATE tracked_products
            SET last_known_price = ?
            WHERE asin = ? AND user_id = (
                SELECT id FROM users WHERE telegram_id = ?
            )
            """, (new_price, asin, telegram_id))
            await db.commit()
    
    async def get_price(self, telegram_id, asin):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("""
            SELECT last_known_price
            FROM tracked_products
            WHERE asin = ? AND user_id = (
                SELECT id FROM users WHERE telegram_id = ?
            )
            """, (asin, telegram_id)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    async def remove_product(self, telegram_id, asin):  
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
            DELETE FROM tracked_products
            WHERE asin = ? AND user_id = (
                SELECT id FROM users WHERE telegram_id = ?
            )
            """, (asin, telegram_id))
            await db.commit()
    
    async def get_tracked_products(self, telegram_id):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("""
            SELECT asin
            FROM tracked_products
            WHERE user_id = (
                SELECT id FROM users WHERE telegram_id = ?
            )
            """, (telegram_id,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
