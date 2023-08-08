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
from aiogram.utils import callback_data
from config import token
import cv2

TOKEN = token


class Reg(StatesGroup):
    state_name = State()
    state_image = State()


class ImageCompare(StatesGroup):
    image = State()

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
        aum.text("Hi"),
    ), reply_markup=nav.MainMenu
    )


'''@dp.callback_query_handler(text="Add someone's photo")
async def get_photo(call: types.CallbackQuery):
    await call.message.answer("Hey! Write a name of a person!", reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await Reg.state_name.set()
    #global photo_name
    #photo_name = await call.answer()'''

@dp.message_handler(text="Add someone's photo")
async def get_photo(message: types.Message):
    await message.answer("Hey! Write a name of a person!", reply_markup=types.ReplyKeyboardRemove())
    #await message.answer()
    await Reg.state_name.set()


@dp.message_handler(state=Reg.state_name, content_types=['text'])
async def get_photo_name(message: types.Message, state: FSMContext):
    await state.update_data(state_name = message.text)
    await message.answer("Hey! Upload a photo of a person!")
    #await message.answer()
    await Reg.state_image.set()


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

    await message.photo[-1].download(destination="img/"+name+".jpg", make_dirs=False)
    print(name)
    await state.finish()
    await message.answer("Thank you! Photo is uploaded successfully", reply_markup=nav.MainMenu)



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
    #for face_loc, name in zip(face_locations, face_names):
    #    print(face_loc)

    await message.bot.send_message(message.from_user.id, f"We found this guy: {face_names}", reply_markup=nav.MainMenu)
    await state.finish()


@dp.message_handler(content_types=['photo'])
async def get_photo(message: types.Message):
    pass
    #global photo_name
    #await message.photo[-1].download('img/' + photo_name + '.jpg')
    #photo_name = ""

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)