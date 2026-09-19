# noinspection PyPep8Naming
from l10n import LocaleKeys as LK, get_available_languages

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, User

from bottypes import ExtendedIKB, ExtendedIKM


# "Reply through logger" markup builder
def event_log_markup_builder(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Reply to {f'@{user.username}' if user.username else user.first_name}",
                              callback_data=f"reply_through_logger_{user.id}")]
    ])


# Back button
back_button = ExtendedIKB(LK.bot_back, selectable=False)

# Channel link for inline messages
inline_button_channel_link = ExtendedIKB(LK.bot_author_text, url=LK.bot_author_link)

markup_inline_button = ExtendedIKM([[inline_button_channel_link]])

# Default
_server_stats = ExtendedIKB(LK.bot_servers_stats)
_profile_info = ExtendedIKB(LK.bot_profile_info)
_extra_features = ExtendedIKB(LK.bot_extras)
_settings = ExtendedIKB(LK.bot_settings)
_help = ExtendedIKB(LK.bot_help_button_title)

main_markup = ExtendedIKM([
    [_server_stats],
    [_profile_info],
    [_extra_features],
    [_settings],
    [_help]
])

# Server Statistics
_server_status = ExtendedIKB(LK.game_status_button_title)
_matchmaking = ExtendedIKB(LK.stats_matchmaking_button_title)
_dc = ExtendedIKB(LK.dc_status_title)

ss_markup = ExtendedIKM([
    [_server_status],
    [_matchmaking],
    [_dc],
    [back_button]
])


# Profile Information
_profile_info = ExtendedIKB(LK.user_profileinfo_title)
_cs_stats = ExtendedIKB(LK.user_gamestats_button_title)

profile_markup = ExtendedIKM([
    [_profile_info],
    [_cs_stats],
    [back_button]
])

# Extra Features

_crosshair = ExtendedIKB(LK.crosshair)
_currency = ExtendedIKB(LK.exchangerate_button_title)
_valve_hq_time = ExtendedIKB(LK.valve_hqtime_button_title)
_timer = ExtendedIKB(LK.game_dropcap_button_title)
_game_version = ExtendedIKB(LK.game_version_button_title)
_leaderboard = ExtendedIKB(LK.game_leaderboard_button_title, selectable=False)
_guns = ExtendedIKB(LK.gun_button_text)

extra_markup = ExtendedIKM([
    [_crosshair, _currency, _game_version],
    [_valve_hq_time, _timer],
    [_leaderboard, _guns],
    [back_button]
])

# Settings

_language = ExtendedIKB(LK.settings_language_button_title)
settings_markup = ExtendedIKM([
    [_language],
    [back_button]
])

# Help

_about_us = ExtendedIKB(LK.bot_aboutus_button_title)
_feedback = ExtendedIKB(LK.bot_feedback_button_title)
help_markup = ExtendedIKM([
    [_about_us],
    [_feedback],
    [back_button]
])

# DC

_europe = ExtendedIKB(LK.regions_europe)
_asia = ExtendedIKB(LK.regions_asia)
_africa = ExtendedIKB(LK.regions_africa)
_south_america = ExtendedIKB(LK.regions_southamerica)
_australia = ExtendedIKB(LK.regions_australia)
_us = ExtendedIKB(LK.dc_us)

dc_markup = ExtendedIKM([
    [_asia, _australia, _europe],
    [_africa, _south_america, _us],
    [back_button]
])

# DC Asia

_china = ExtendedIKB(LK.regions_china)
_emirates = ExtendedIKB(LK.dc_emirates)
_hongkong = ExtendedIKB(LK.dc_hongkong)
_india = ExtendedIKB(LK.dc_india)
_japan = ExtendedIKB(LK.dc_japan)
_singapore = ExtendedIKB(LK.dc_singapore)
_south_korea = ExtendedIKB(LK.dc_southkorea)

dc_asia_markup = ExtendedIKM([
    [_china, _emirates, _hongkong],
    [_india, _japan],
    [_singapore, _south_korea],
    [back_button]
])

# DC Europe

_austria = ExtendedIKB(LK.dc_austria)
_finland = ExtendedIKB(LK.dc_finland)
_germany = ExtendedIKB(LK.dc_germany)
# _netherlands = ExtendedIKB(LK.dc_netherlands)
_poland = ExtendedIKB(LK.dc_poland)
_spain = ExtendedIKB(LK.dc_spain)
_sweden = ExtendedIKB(LK.dc_sweden)
_uk = ExtendedIKB(LK.dc_uk)

dc_eu_markup = ExtendedIKM([
    [_austria, _finland, _germany],
    [_poland, _spain],
    [_sweden, _uk],
    [back_button]
])

# DC USA

_us_east = ExtendedIKB(LK.dc_east, callback_data=LK.dc_us_east)
_us_west = ExtendedIKB(LK.dc_west, callback_data=LK.dc_us_west)
_us_south = ExtendedIKB(LK.dc_south, callback_data=LK.dc_us_south)

dc_us_markup = ExtendedIKM([
    [_us_east, _us_west, _us_south],
    [back_button]
])

# DC South America

_argentina = ExtendedIKB(LK.dc_argentina)
_brazil = ExtendedIKB(LK.dc_brazil)
_chile = ExtendedIKB(LK.dc_chile)
_peru = ExtendedIKB(LK.dc_peru)

dc_southamerica_markup = ExtendedIKM([
    [_argentina, _brazil],
    [_chile, _peru],
    [back_button]
])

# Guns

_pistols = ExtendedIKB(LK.gun_pistols)
_heavy = ExtendedIKB(LK.gun_heavy)
_smgs = ExtendedIKB(LK.gun_smgs)
_rifles = ExtendedIKB(LK.gun_rifles)

guns_markup = ExtendedIKM([
    [_pistols, _heavy],
    [_smgs, _rifles],
    [back_button]
])

# Pistols

_usps = ExtendedIKB("USP-S", callback_data="usps", translatable=False)
_p2000 = ExtendedIKB("P2000", callback_data="p2000", translatable=False)
_glock = ExtendedIKB("Glock-18", callback_data="glock18", translatable=False)
_dualies = ExtendedIKB("Dual Berettas", callback_data="dualberettas", translatable=False)
_p250 = ExtendedIKB("P250", callback_data="p250", translatable=False)
_cz75 = ExtendedIKB("CZ75-Auto", callback_data="cz75auto", translatable=False)
_five_seven = ExtendedIKB("Five-SeveN", callback_data="fiveseven", translatable=False)
_tec = ExtendedIKB("Tec-9", callback_data="tec9", translatable=False)
_deagle = ExtendedIKB("Desert Eagle", callback_data="deserteagle", translatable=False)
_r8 = ExtendedIKB("R8 Revolver", callback_data="r8revolver", translatable=False)

pistols_markup = ExtendedIKM([
    [_usps, _p2000, _glock],
    [_dualies, _p250],
    [_five_seven, _tec, _cz75],
    [_deagle, _r8],
    [back_button]
])

# Heavy

_nova = ExtendedIKB("Nova", callback_data="nova", translatable=False)
_xm1014 = ExtendedIKB("XM1014", callback_data="xm1014", translatable=False)
_mag7 = ExtendedIKB("MAG-7", callback_data="mag7", translatable=False)
_sawedoff = ExtendedIKB("Sawed-Off", callback_data="sawedoff", translatable=False)
_m249 = ExtendedIKB("M249", callback_data="m249", translatable=False)
_negev = ExtendedIKB("Negev", callback_data="negev", translatable=False)

heavy_markup = ExtendedIKM([
    [_nova, _xm1014],
    [_mag7, _sawedoff],
    [_m249, _negev],
    [back_button],
])

# SMGs

_mp9 = ExtendedIKB("MP9", callback_data="mp9", translatable=False)
_mac10 = ExtendedIKB("MAC-10", callback_data="mac10", translatable=False)
_mp7 = ExtendedIKB("MP7", callback_data="mp7", translatable=False)
_mp5 = ExtendedIKB("MP5-SD", callback_data="mp5sd", translatable=False)
_ump = ExtendedIKB("UMP-45", callback_data="ump45", translatable=False)
_p90 = ExtendedIKB("P90", callback_data="p90", translatable=False)
_pp = ExtendedIKB("PP-Bizon", callback_data="ppbizon", translatable=False)

smgs_markup = ExtendedIKM([
    [_mp9, _mac10],
    [_mp7, _mp5],
    [_ump, _p90, _pp],
    [back_button]
])

# Rifles

_famas = ExtendedIKB("FAMAS", callback_data="famas", translatable=False)
_galil = ExtendedIKB("Galil AR", callback_data="galilar", translatable=False)
_m4a4 = ExtendedIKB("M4A4", callback_data="m4a4", translatable=False)
_m4a1 = ExtendedIKB("M4A1-S", callback_data="m4a1s", translatable=False)
_ak = ExtendedIKB("AK-47", callback_data="ak47", translatable=False)
_aug = ExtendedIKB("AUG", callback_data="aug", translatable=False)
_sg = ExtendedIKB("SG 553", callback_data="sg553", translatable=False)
_ssg = ExtendedIKB("SSG 08", callback_data="ssg08", translatable=False)
_awp = ExtendedIKB("AWP", callback_data="awp", translatable=False)
_scar = ExtendedIKB("SCAR-20", callback_data="scar20", translatable=False)
_g3sg1 = ExtendedIKB("G3SG1", callback_data="g3sg1", translatable=False)

rifles_markup = ExtendedIKM([
    [_famas, _galil],
    [_m4a4, _m4a1, _ak],
    [_aug, _sg],
    [_ssg, _awp],
    [_scar, _g3sg1],
    [back_button]
])

# Leaderboard

_leaderboard_global = ExtendedIKB(LK.game_leaderboard_world)
_leaderboard_na = ExtendedIKB(LK.regions_northamerica)
_leaderboard_sa = ExtendedIKB(LK.regions_southamerica)
_leaderboard_eu = ExtendedIKB(LK.regions_europe)
_leaderboard_as = ExtendedIKB(LK.regions_asia)
_leaderboard_au = ExtendedIKB(LK.regions_australia)
_leaderboard_china = ExtendedIKB(LK.regions_china)
_leaderboard_af = ExtendedIKB(LK.regions_africa)

leaderboard_markup = ExtendedIKM([
    [_leaderboard_global],
    [_leaderboard_na, _leaderboard_sa],
    [_leaderboard_eu, _leaderboard_as],
    [_leaderboard_au, _leaderboard_af],
    [_leaderboard_china],
    [back_button]
])

# Crosshair

_generate_crosshair = ExtendedIKB(LK.crosshair_generate, callback_data=LK.crosshair_generate)
_decode_crosshair = ExtendedIKB(LK.crosshair_decode, callback_data=LK.crosshair_decode)

crosshair_markup = ExtendedIKM([
    [_generate_crosshair, _decode_crosshair],
    [back_button]
])


# Language

def get_language_settings_layout():
    available_langs = get_available_languages()
    columns = 3

    language_buttons = []
    row = []
    for lang_code, lang_name in available_langs.items():
        row.append(ExtendedIKB(lang_name, callback_data=lang_code, translatable=False))
        if len(row) >= columns:
            language_buttons.append(row)  # yes, we append lists
            row = []
    if row:
        language_buttons.append(row)

    language_buttons.append([back_button])
    return language_buttons


language_settings_markup = ExtendedIKM(get_language_settings_layout())

all_selectable_markups = (ss_markup, extra_markup,
                          dc_markup, dc_asia_markup, dc_eu_markup, dc_us_markup, dc_southamerica_markup,
                          pistols_markup, heavy_markup, smgs_markup, rifles_markup, language_settings_markup)
