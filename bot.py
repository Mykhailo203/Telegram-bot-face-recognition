import os
import pathlib
from io import IOBase

from simple_facerec import SimpleFacerec
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import  MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import markups as nav
import aiogram.utils.markdown as aum
import PostgreSQL
from config import token

TOKEN = token


class Reg(StatesGroup):
    state_name = State()
    state_image = State()


class ImageCompare(StatesGroup):
    image = State()


class ImageUpdate(StatesGroup):
    new_name = State()
    new_image = State()

class RegUkr(StatesGroup):
    state_name = State()
    state_image = State()


class ImageCompareUkr(StatesGroup):
    image = State()


class ImageUpdateUkr(StatesGroup):
    new_name = State()
    new_image = State()


bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands="start")
async def start_handler(message: types.Message):
    p = PostgreSQL.select("SELECT * FROM users WHERE telegramid = (%s)", (message['from']['id'],))
    if len(p) == 0:
        PostgreSQL.execute("""INSERT into users(name, telegramid) VALUES (%s, %s)""",
                           (message.from_user.full_name, message['from']['id'],))
    else:
        print("Не реєструємо")
    await message.reply(aum.text(
        aum.text("Hi! I am going to help you with face recognition!\n"),
        aum.text("There are three functions: you can add people, recognize them, and update already added person's info!\n"),
        aum.text("Choose a language you would be comfortable with.")
    ), reply_markup=nav.ChooseLanguage
    )

#English version
@dp.message_handler(text="Change to english")
async def english(message: types.Message):
    await message.answer("English is such a beautiful language! Use buttons to continue", reply_markup=nav.MainMenu)


@dp.message_handler(text="Add someone's photo")
async def get_photo(message: types.Message):
    await message.answer("Hey! Write a name of a person!", reply_markup=types.ReplyKeyboardRemove())
    await Reg.state_name.set()


@dp.message_handler(state=Reg.state_name, content_types=types.ContentTypes.ANY)
async def get_photo_name(message: types.Message, state: FSMContext):
    if message.sticker:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()
    elif message.text:

        await state.update_data(state_name=message.text)
        await message.answer("Thank you! Upload a photo of a person!")
        await Reg.state_image.set()
    else:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()


@dp.message_handler(state=Reg.state_image, content_types=['photo'])
async def get_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["state_name"]
        image = message.photo

    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination

    await message.photo[-1].download(destination="img_check/" + str(name) + ".jpg", make_dirs=False)
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_check/" + str(name) + ".jpg")
    if "Unknown" in face_names:
        os.remove("img_check/" + str(name) + ".jpg")
        await message.photo[-1].download(destination="img/" + str(name) + ".jpg", make_dirs=False)
        await state.finish()
        await message.answer("Thank you! Photo is uploaded successfully", reply_markup=nav.MainMenu)
    elif len(face_names) == 0:
        os.remove("img_check/" + str(name) + ".jpg")
        await state.finish()
        await message.answer("Oops! I didn't find a person on your photo :/ Try again!", reply_markup=nav.MainMenu)
    elif len(face_names) > 1:
        os.remove("img_check/" + str(name) + ".jpg")
        await state.finish()
        await message.answer("Oops! There is more than 1 person on this image. Maybe you wanted to recognize them?", reply_markup=nav.MainMenu)
    else:
        os.remove("img_check/" + str(name) + ".jpg")
        await state.finish()
        await message.answer("Oops! That person has been already added :/ Probably you wanted to recognize someone?",
                             reply_markup=nav.MainMenu)
        print(len(face_names), face_names)


@dp.message_handler(text="Recognize someone")
async def start_handler(message: types.Message):
    await message.reply(aum.text(
        aum.text("Hi, upload a photo of a person you want to recognize"),
    ), reply_markup=types.ReplyKeyboardRemove()
    )
    await ImageCompare.image.set()


@dp.message_handler(state=ImageCompare.image, content_types=['photo'])
async def get_photo_to_recognize(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        image = message.photo
    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination

    await message.photo[-1].download("img_compare/"+str(message['from']['id'])+".jpg")
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_compare/"+str(message['from']['id'])+".jpg")
    l = len(face_names)
    await message.bot.send_message(message.from_user.id, f"I found {l} people! And i found this person(s): {face_names}", reply_markup=nav.MainMenu)
    await state.finish()

@dp.message_handler(text="Update Image")
async def update_photo(message: types.Message):
    await message.answer("Write a new name for your person(if you don't want to change it just send 'same as last')", reply_markup=types.ReplyKeyboardRemove())
    await ImageUpdate.new_name.set()


@dp.message_handler(state=ImageUpdate.new_name, content_types=types.ContentTypes.ANY)
async def get_new_photo_name(message: types.Message, state: FSMContext):
    if message.sticker:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()
    elif message.text:
        await state.update_data(new_name=message.text)
        await message.answer("Thank you! Upload a photo of a person!")
        await ImageUpdate.new_image.set()
    else:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()


@dp.message_handler(state=ImageUpdate.new_image, content_types=['photo'])
async def get_new_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["new_name"]
        image = message.photo

    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination
    await message.photo[-1].download(destination="img_check/" + str(message['from']['id']) + str(name) + ".jpg", make_dirs=False)
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_check/" + str(message['from']['id']) + str(name) + ".jpg")
    if "Unknown" in face_names:
        os.remove("img_check/" + str(message['from']['id']) + str(name) + ".jpg")
        await state.finish()
        await message.answer("Unknown person. Probably you wanted to add this person?", reply_markup=nav.MainMenu)
    elif len(face_names) == 0:
        os.remove("img_check/" + str(message['from']['id']) + str(name) + ".jpg")
        await state.finish()
        await message.answer("Oops! I didn't find a person on your photo :/ Try again!", reply_markup=nav.MainMenu)
    elif len(face_names) > 1:
        os.remove("img_check/" + str(message['from']['id']) + str(name) + ".jpg")
        await state.finish()
        await message.answer("Oops! There is more than 1 person on this image. Maybe you wanted to recognize them?", reply_markup=nav.MainMenu)
    else:
        os.remove("img_check/" + str(message['from']['id']) + str(name) + ".jpg")
        if name == 'same as last' or 'Same as last':
            real_name = face_names[0]
            await message.photo[-1].download(destination="img/" + str(real_name) + ".jpg",
                                             make_dirs=False)
            await state.finish()
            await message.answer(
                f"Photo was updated successfully with {real_name} name",
                reply_markup=nav.MainMenu)
        else:
            real_name = face_names[0]
            os.remove("img/" + str(real_name) + ".jpg")
            await message.photo[-1].download(destination="img/" + str(name) + ".jpg",
                                             make_dirs=False)
            await message.answer(
                f"Photo was updated successfully with {name} name",
                reply_markup=nav.MainMenu)
            await state.finish()


# Ukrainian version
@dp.message_handler(text="Змінити на українську")
async def english(message: types.Message):
    await message.answer("Українська-солов'їна. Використовуйте кнопки щоб продовжити", reply_markup=nav.MainMenu_ukr)


@dp.message_handler(text="Додати людину")
async def get_photo(message: types.Message):
    await message.answer("Привіт! Введи ім'я людини", reply_markup=types.ReplyKeyboardRemove())
    await RegUkr.state_name.set()


@dp.message_handler(state=RegUkr.state_name, content_types=types.ContentTypes.ANY)
async def get_photo_name(message: types.Message, state: FSMContext):
    try:
        if message.sticker:
            await message.answer("Мені треба ім'я!", reply_markup=nav.MainMenu_ukr)
            await state.finish()
        elif message.text:
            await state.update_data(state_name=message.text)
            await message.answer("Гарне ім'я! Завантажте фото людини")
            await RegUkr.state_image.set()
        else:
            await message.answer("Мені треба ім'я!", reply_markup=nav.MainMenu_ukr)
            await state.finish()
    except:
        await message.answer("Ім'я можна вводити тільки англійською. Вибачаюсь за незручності!:(")
        await state.finish()


@dp.message_handler(state=RegUkr.state_image, content_types=['photo'])
async def get_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["state_name"]
        image = message.photo

    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination

    await message.photo[-1].download(destination="img_check/" + str(message['from']['id']) + ".jpg", make_dirs=False)
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_check/" + str(message['from']['id']) + ".jpg")
    if "Unknown" in face_names:
        os.remove("img_check/" + str(message['from']['id']) + ".jpg")
        await message.photo[-1].download(destination="img/" + str(name) + ".jpg", make_dirs=False)
        await state.finish()
        await message.answer("Дякую! Фото було успішно завантажено!", reply_markup=nav.MainMenu_ukr)
    elif len(face_names) == 0:
        os.remove("img_check/" + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Упс! Я не знайшов людини на вашому фото:( Спробуйте ще раз", reply_markup=nav.MainMenu_ukr)
    elif len(face_names) > 1:
        os.remove("img_check/" + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Упс! На цьому фото більш ніж одна людина, можливо ви хотіли розпізнати їх?",
                             reply_markup=nav.MainMenu_ukr)
    else:
        os.remove("img_check/" + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Упс! Ця людина вже була додана! Можливо ви хотіли оновити інформацію про цю людину?",
                             reply_markup=nav.MainMenu_ukr)
        print(len(face_names), face_names)


@dp.message_handler(text="Розпізнати людину")
async def start_handler(message: types.Message):
    await message.reply(aum.text(
        aum.text("Привіт! Завантаж фотографію людини яку ти хочеш розпізнати."),
    ), reply_markup=types.ReplyKeyboardRemove()
    )
    await ImageCompareUkr.image.set()


@dp.message_handler(state=ImageCompareUkr.image, content_types=['photo'])
async def get_photo_to_recognize(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        image = message.photo

    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination

    await message.photo[-1].download("img_compare/" + str(message['from']['id']) + ".jpg")
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_compare/" + str(message['from']['id']) + ".jpg")
    l = len(face_names)
    await message.bot.send_message(message.from_user.id,
                                   f"Я знайшов {l} людей! А саме їх: {face_names}",
                                   reply_markup=nav.MainMenu_ukr)
    await state.finish()


@dp.message_handler(text="Оновити інфо про вже додану людину")
async def update_photo(message: types.Message):
    await message.answer("Напиши нове ім'я для твоєї людини(Якщо не хочеш міняти ім'я, то просто напиши 'same as last')",
                         reply_markup=types.ReplyKeyboardRemove())
    await ImageUpdateUkr.new_name.set()


@dp.message_handler(state=ImageUpdateUkr.new_name, content_types=types.ContentTypes.ANY)
async def get_new_photo_name(message: types.Message, state: FSMContext):
    if message.sticker:
        await message.answer("Мені треба ім'я!", reply_markup=nav.MainMenu_ukr)
        await state.finish()
    elif message.text:
        await state.update_data(new_name=message.text)
        await message.answer("Дякую! Завантаж фото людини")
        await ImageUpdateUkr.new_image.set()
    else:
        await message.answer("Мені треба ім'я!", reply_markup=nav.MainMenu_ukr)
        await state.finish()


@dp.message_handler(state=ImageUpdateUkr.new_image, content_types=['photo'])
async def get_new_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["new_name"]
        image = message.photo

    async def _prepare_destination(self, destination, make_dirs):
        file = await self.get_file()

        if destination is None:
            return file, destination

        if isinstance(destination, IOBase):
            return file, destination

        if not isinstance(destination, (str, pathlib.Path)):
            raise TypeError("destination must be str, pathlib.Path or io.IOBase type")

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

        return file, destination

    await message.photo[-1].download(destination="img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg",
                                     make_dirs=False)
    sfr = SimpleFacerec()
    sfr.load_encoding_images("img/")
    face_locations, face_names = sfr.detect_known_faces("img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg")
    if "Unknown" in face_names:
        os.remove("img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Невідома людина! Можливо ви хотіли додати цю людину?", reply_markup=nav.MainMenu_ukr)
    elif len(face_names) == 0:
        os.remove("img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Упс! Я не знайшов людини на вашому фото:( Спробуйте ще раз!", reply_markup=nav.MainMenu_ukr)
    elif len(face_names) > 1:
        os.remove("img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg")
        await state.finish()
        await message.answer("Упс! На цьому фото більш ніж одна людина, можливо ви хотіли розпізнати їх?",
                             reply_markup=nav.MainMenu_ukr)
    else:
        os.remove("img_check/" + str(message['from']['id']) + str(message['from']['id']) + ".jpg")
        if name == 'same as last' or 'Same as last':
            real_name = face_names[0]
            await message.photo[-1].download(destination="img/" + str(real_name) + ".jpg",
                                             make_dirs=False)
            await state.finish()
            await message.answer(
                f"Фото було успішно оновлено з {real_name} ім'ям",
                reply_markup=nav.MainMenu_ukr)
        else:
            real_name = face_names[0]
            os.remove("img/" + str(real_name) + ".jpg")
            await message.photo[-1].download(destination="img/" + str(name) + ".jpg",
                                             make_dirs=False)
            await message.answer(
                f"Фото було успішно оновлено з {name} ім'ям",
                reply_markup=nav.MainMenu_ukr)
            await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)