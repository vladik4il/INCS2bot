from copy import deepcopy

from pyrogram.enums import ButtonStyle
from pyrogram.types import (CallbackGame,
                            InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            LoginUrl,
                            WebAppInfo, CopyTextButton, SwitchInlineQueryChosenChat, DisabledButton)

from l10n import Locale


__all__ = ('ExtendedIKB', 'ExtendedIKM')


class ExtendedIKB(InlineKeyboardButton):
    SELECTION_INDICATOR = '•'

    def __init__(self,
                 text: str,
                 *,
                 icon_custom_emoji_id: str | None = None,
                 style: ButtonStyle = ButtonStyle.DEFAULT,
                 url: str | None = None,
                 callback_data: str | bytes | None = None,
                 requires_password: bool | None = None,
                 web_app: WebAppInfo | None = None,
                 login_url: LoginUrl | None = None,
                 user_id: int | None = None,
                 switch_inline_query: str | None = None,
                 switch_inline_query_current_chat: str | None = None,
                 switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = None,
                 copy_text: CopyTextButton | None = None,
                 callback_game: CallbackGame | None = None,
                 pay: bool | None = None,
                 disabled: DisabledButton | None = None,
                 translatable: bool = True,
                 selectable: bool = True):
        if callback_data is None and url is None:
            callback_data = text

        super().__init__(text=text, icon_custom_emoji_id=icon_custom_emoji_id, url=url, style=style,
                         callback_data=callback_data, requires_password=requires_password, web_app=web_app,
                         login_url=login_url, user_id=user_id,  switch_inline_query=switch_inline_query,
                         switch_inline_query_current_chat=switch_inline_query_current_chat,
                         switch_inline_query_chosen_chat=switch_inline_query_chosen_chat, copy_text=copy_text,
                         callback_game=callback_game, pay=pay, disabled=disabled)
        self.translatable = translatable
        self.selectable = selectable

        self.text_key = self.text
        self.url_key = None
        self.selected = False
        if self.url:
            self.url_key = self.url

    def set_localed_text(self, locale: Locale):
        if self.translatable:
            self.text = locale.get(self.text_key)
            if self.url_key:
                self.url = locale.get(self.url_key)
        else:
            self.text = self.text_key

        if self.selectable and self.selected:
            self.text = f'{self.SELECTION_INDICATOR} {self.text} {self.SELECTION_INDICATOR}'

    def localed(self, locale: Locale):
        copy = deepcopy(self)
        copy.set_localed_text(locale)
        return copy

    def __call__(self, locale: Locale):
        return self.localed(locale)


class ExtendedIKM(InlineKeyboardMarkup):
    def iter_buttons(self):
        for line in self.inline_keyboard:
            for button in line:
                yield button

    def update_locale(self, locale: Locale):
        for button in self.iter_buttons():
            if isinstance(button, ExtendedIKB):
                button.set_localed_text(locale)

    def localed(self, locale: Locale):
        copy = deepcopy(self)
        copy.update_locale(locale)
        return copy

    def __call__(self, locale: Locale):
        return self.localed(locale)

    def select_button_by_key(self, key: str):
        for button in self.iter_buttons():
            if isinstance(button, ExtendedIKB) and button.selectable:
                button.selected = (button.text_key == key or button.callback_data == key)
