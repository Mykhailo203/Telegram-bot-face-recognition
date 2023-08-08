from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_main = KeyboardButton('Main menu')

btn_add_photo = KeyboardButton("Add someone's photo")
btn_recognize = KeyboardButton("Recognize someone")
MainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_photo, btn_recognize)