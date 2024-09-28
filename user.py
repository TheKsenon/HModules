from .. import loader, utils
from telethon.tl.types import Message
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
import re
import asyncio

@loader.tds
class UserInfoMod(loader.Module):
    strings = {
        "name": "UserInfo",
        "userinfo_cmd_desc": "Показывает основную информацию о пользователе",
        "advancedinfo_cmd_desc": "Показывает расширенную информацию о пользователе, включая данные от @funstat_obot"
    }
    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.owner
    async def userinfocmd(self, message):
        await message.edit("👁️‍🗨️ Загружаю информацию...")
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        try:
            if args:
                user = await self.client.get_entity(args)
            elif reply:
                user = await self.client.get_entity(reply.sender_id)
            else:
                await message.edit("Пожалуйста, укажите пользователя или ответьте на его сообщение.")
                return
            full_user = await self.client(GetFullUserRequest(user.id))
            main_text = self.get_main_text(user, full_user)
            await self.inline.form(
                message=message,
                text=main_text,
                reply_markup=[
                    [{"text": "🔧 Подробнее", "callback": self.detail_callback, "args": (user.id,)}],
                ],
                photo="https://i.imgur.com/Ylwy6Gh.jpeg",
                disable_security=True,
            )
        except Exception as e:
            await message.edit(f"Произошла ошибка: {str(e)}")

    @loader.owner
    async def advancedinfocmd(self, message):
        await message.edit("👁️‍🗨️ Загружаю расширенную информацию...")
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        try:
            if args:
                user = await self.client.get_entity(args)
            elif reply:
                user = await self.client.get_entity(reply.sender_id)
            else:
                await message.edit("Пожалуйста, укажите пользователя, ID или ответьте на сообщение.")
                return
            full_user = await self.client(GetFullUserRequest(user.id))
            funstat_data = await self.get_funstat_data(user.username or user.id)
            if not funstat_data:
                await message.edit("Не удалось получить информацию от @funstat_obot.")
                return
            advanced_text = self.get_advanced_text(user, full_user, funstat_data)
            await self.inline.form(
                message=message,
                text=advanced_text,
                reply_markup=[
                    [{"text": "🔧 Подробнее", "callback": self.advanced_detail_callback, "args": (user.id,)}],
                ],
                photo="https://i.imgur.com/Ylwy6Gh.jpeg",
                disable_security=True,
            )
        except Exception as e:
            await message.edit(f"Произошла ошибка: {str(e)}")

    def get_main_text(self, user, full_user):
        return (
            f"👤 Информация о пользователе:\n\n"
            f"[+] Имя: <b>{utils.escape_html(user.first_name)}</b>\n"
            f"[+] Фамилия: <b>{utils.escape_html(user.last_name or 'Не указана')}</b>\n"
            f"[+] ID: <b><a href='tg://user?id={user.id}'>{user.id}</a></b>\n"
            f"[+] Юзернейм: <b>{('@' + user.username) if user.username else 'Отсутствует'}</b>\n"
            f"[+] Бот: <b>{'Да' if user.bot else 'Нет'}</b>\n"
            f"[+] Есть премиум: <b>{'Да' if user.premium else 'Нет'}</b>\n"
            f"[+] Верифицирован: <b>{'Да' if user.verified else 'Нет'}</b>\n\n"
            f"[+] Описание: <b>{utils.escape_html(full_user.full_user.about or 'Не указано')}</b>"
        )

    def get_detail_text(self, user):
        return (
            f"👤 Подробнее:\n\n"
            f"[+] Внутренний: <b>{'Да' if user.is_self else 'Нет'}</b>\n"
            f"[+] Ваш контакт: <b>{'Да' if user.contact else 'Нет'}</b>\n"
            f"[+] Взаимный контакт: <b>{'Да' if user.mutual_contact else 'Нет'}</b>\n"
            f"[+] Удаленный аккаунт: <b>{'Да' if user.deleted else 'Нет'}</b>\n"
            f"[+] Бот: <b>{'Да' if user.bot else 'Нет'}</b>\n"
            f"[+] История: <b>{'Да' if user.bot_chat_history else 'Нет'}</b>\n"
            f"[+] Без истории: <b>{'Да' if user.bot_nochats else 'Нет'}</b>\n"
            f"[+] Официальный аккаунт: <b>{'Да' if user.verified else 'Нет'}</b>\n"
            f"[+] Ограниченный: <b>{'Да' if user.restricted else 'Нет'}</b>\n"
            f"[+] Мин: <b>{'Да' if user.min else 'Нет'}</b>\n"
            f"[+] Геолокация: <b>{'Да' if user.bot_inline_geo else 'Нет'}</b>\n"
            f"[+] Поддержка телеги: <b>{'Да' if user.support else 'Нет'}</b>\n"
            f"[+] Скам-аккаунт: <b>{'Да' if user.scam else 'Нет'}</b>\n"
            f"[+] apply_min_photo: <b>{'Да' if user.apply_min_photo else 'Нет'}</b>\n"
            f"[+] Фэйк аккаунт: <b>{'Да' if user.fake else 'Нет'}</b>\n"
            f"[+] Меню в боте: <b>{'Да' if user.bot_attach_menu else 'Нет'}</b>\n"
            f"[+] Премиум: <b>{'Да' if user.premium else 'Нет'}</b>\n"
            f"[+] Меню: <b>{'Да' if user.attach_menu_enabled else 'Нет'}</b>\n"
            f"[+] Изменять сообщения: <b>{'Да' if user.bot_can_edit else 'Нет'}</b>\n"
            f"[+] Номер: <b>{user.phone or 'Не указан'}</b>"
        )

    async def get_funstat_data(self, user_identifier):
        funstat_bot = await self.client.get_entity("@funstat_obot")
        if isinstance(user_identifier, str) and not user_identifier.startswith('@'):
            user_identifier = '@' + user_identifier
        await self.client.send_message(funstat_bot, str(user_identifier))
        for _ in range(30):
            async for message in self.client.iter_messages(funstat_bot, limit=1):
                if "Это" in message.text:
                    funstat_response = message.text
                    # Удаляем всю историю чата с ботом
                    await self.client(DeleteHistoryRequest(peer=funstat_bot, max_id=0, just_clear=True, revoke=True))
                    return self.parse_funstat_data(funstat_response)
            await asyncio.sleep(1)
        return None

    def parse_funstat_data(self, response):
        data = {}
        full_name_match = re.search(r"Это (.*)", response)
        data['full_name'] = full_name_match.group(1) if full_name_match else "Не удалось получить"

        message_count_match = re.search(r"(\d+) сообщ", response)
        chat_count_match = re.search(r"в (\d+) чат", response)
        data['message_count'] = message_count_match.group(1) if message_count_match else "Не удалось получить"
        data['chat_count'] = chat_count_match.group(1) if chat_count_match else "Не удалось получить"

        favorite_chat_match = re.search(r"Любимый чат: (.*?)(?:\n|$)", response, re.DOTALL)
        data['favorite_chat'] = favorite_chat_match.group(1).strip() if favorite_chat_match else "Не удалось получить"

        data['usernames'] = re.findall(r"\| (@\w+)", response)

        names_match = re.search(r"Имена:(.*?)(?:\n\n|\Z)", response, re.DOTALL)
        if names_match:
            names_text = names_match.group(1).strip()
            data['names'] = re.findall(r"\|- [\d.]+ -> (.*)", names_text)
        else:
            data['names'] = []

        return data

    def get_advanced_text(self, user, full_user, funstat_data):
        if not funstat_data:
            return f"👤 [ADVANCED] Информация:\n\nНе удалось получить данные от @funstat_obot."

        names_text = self.format_list(funstat_data['names']) if funstat_data['names'] else "— Не менялись."
        usernames_text = self.format_list(funstat_data['usernames']) if funstat_data['usernames'] else "— @" + user.username if user.username else "— Отсутствуют."

        message_count = funstat_data.get('message_count')
        chat_count = funstat_data.get('chat_count')
        message_info = f"[+] <b>{message_count}</b> сообщ. в <b>{chat_count}</b> чат.\n" if message_count != "Не удалось получить" and chat_count != "Не удалось получить" else ""

        return (
            f"👤 [ADVANCED] Информация:\n\n"
            f"[+] Имя: <b>{utils.escape_html(user.first_name)}</b>\n"
            f"[+] Фамилия: <b>{utils.escape_html(user.last_name or 'Не указана')} 🍰</b>\n"
            f"[+] ID: <b><a href='tg://user?id={user.id}'>{user.id}</a></b>\n"
            f"[+] Юзернейм: <b>{('@' + user.username) if user.username else 'Отсутствует'}</b>\n"
            f"[+] Бот: <b>{'Да' if user.bot else 'Нет'}</b>\n"
            f"[+] Никнеймы:\n{usernames_text}\n"
            f"[+] Имена:\n{names_text}\n"
            f"[+] Любимый чат: <b>{funstat_data['favorite_chat']}</b>\n"
            f"{message_info}"
            f"[+] Есть премиум: <b>{'Да' if user.premium else 'Нет'}</b>\n"
            f"[+] Верифицирован: <b>{'Да' if user.verified else 'Нет'}</b>\n\n"
            f"[+] Описание: <b>{utils.escape_html(full_user.full_user.about or 'Не указано')}</b>"
        )

    def format_list(self, items):
        if not items:
            return "— Отсутствуют."
        formatted = "\n".join(f"— {item}" for item in items[:3])
        if len(items) > 3:
            formatted += f"\n— ...и еще {len(items) - 3}"
        return formatted

    async def detail_callback(self, call, user_id):
        user = await self.client.get_entity(int(user_id))
        detail_text = self.get_detail_text(user)
        await call.edit(
            text=detail_text,
            reply_markup=[
                [{"text": "⬅️ Назад", "callback": self.back_callback, "args": (user_id,)}],
            ],
        )

    async def advanced_detail_callback(self, call, user_id):
        user = await self.client.get_entity(int(user_id))
        detail_text = self.get_detail_text(user)
        await call.edit(
            text=detail_text,
            reply_markup=[
                [{"text": "⬅️ Назад", "callback": self.advanced_back_callback, "args": (user_id,)}],
            ],
        )

    async def back_callback(self, call, user_id):
        user = await self.client.get_entity(int(user_id))
        full_user = await self.client(GetFullUserRequest(user.id))
        main_text = self.get_main_text(user, full_user)
        await call.edit(
            text=main_text,
            reply_markup=[
                [{"text": "🔧 Подробнее", "callback": self.detail_callback, "args": (user_id,)}],
            ],
        )

    async def advanced_back_callback(self, call, user_id):
        user = await self.client.get_entity(int(user_id))
        full_user = await self.client(GetFullUserRequest(user.id))
        funstat_data = await self.get_funstat_data(user.username or user.id)
        advanced_text = self.get_advanced_text(user, full_user, funstat_data)
        await call.edit(
            text=advanced_text,
            reply_markup=[
                [{"text": "🔧 Подробнее", "callback": self.advanced_detail_callback, "args": (user_id,)}],
            ],
        )
