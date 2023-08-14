"""import os
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



def get_name(message, state, state_name, state_img):
    if message.sticker:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()
    elif message.text:
        await state.update_data(new_name=message.text)
        await message.answer("Thank you! Upload a photo of a person!")
        await ImageUpdate.new_image.set()
    else:
        await message.answer("I need name of a person...", reply_markup=nav.MainMenu)
        await state.finish()"""
