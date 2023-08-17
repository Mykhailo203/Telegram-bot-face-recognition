from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


english = KeyboardButton("Change to english")
ukrainian = KeyboardButton("Змінити на українську")

btn_add_photo_ukr = KeyboardButton("Додати людину")
btn_recognize_ukr = KeyboardButton("Розпізнати людину")
btn_update_ukr = KeyboardButton("Оновити інфо про вже додану людину")
MainMenu_ukr = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_photo_ukr, btn_recognize_ukr, btn_update_ukr, english)


btn_add_photo = KeyboardButton("Add someone's photo")
btn_recognize = KeyboardButton("Recognize someone")
btn_update = KeyboardButton("Update Image")
MainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_photo, btn_recognize, btn_update, ukrainian)


ChooseLanguage = ReplyKeyboardMarkup(resize_keyboard=True).add(english, ukrainian)