from telethon import TelegramClient, events
import sqlite3
import os
from DADOS import *

current_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_directory, 'sangmata_bot.db')
session_path = os.path.join(current_directory, 'my_account.session')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        telegram_id INTEGER
    )
''')

conn.commit()

bot = TelegramClient(session_path, api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    welcome_message = (
        "Bem-vindo ao Bot SangMata!\n\n"
        "Envie o ID de um usuário para receber informações sobre a conta dele."
    )
    await event.respond(welcome_message)

@bot.on(events.NewMessage)
async def handle_message(event):
    try:
        user_id = int(event.raw_text.strip())
        if user_id > 0:
            user = await bot.get_entity(user_id)
            cursor.execute('''
                INSERT INTO user_info (first_name, last_name, username, telegram_id)
                VALUES (?, ?, ?, ?)
            ''', (user.first_name, user.last_name, user.username, user.id))
            conn.commit()
            
            info_message = f"❇️INFORMAÇÕES DA CONTA:\n"
            info_message += f"💎NOME: {user.first_name}\n"
            if user.last_name:
                info_message += f"💎SOBRENOME: {user.last_name}\n"
            info_message += f"💎USERNAME: @{user.username}\n"
            info_message += f"💎ID: {user.id}\n"
            await event.respond(info_message)
        else:
            await event.respond("O ID fornecido não corresponde a um usuário válido!")
    
    except ValueError:
        pass 
    except Exception as e:
        await event.respond(f"Erro ao processar o pedido: {str(e)}")

bot.run_until_disconnected()
conn.close()
