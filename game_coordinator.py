import asyncio
import datetime as dt
import platform
import sys
import time
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from csgo.client import CSGOClient
import gevent
import httpx
from pyrogram import Client
from pyrogram.types import LinkPreviewOptions
from steam.client import SteamClient
from steam.enums import EResult

if platform.system() == 'Linux':
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import uvloop

    uvloop.install()

import config
from functions import caching, locale, utime
from functions.ulogging import *
from utypes import GameVersion, States, GameVersionData

VALVE_TIMEZONE = ZoneInfo('America/Los_Angeles')
loc = locale('ru')

AVAILABLE_ALERTS = {'public_branch_updated': loc.notifs_build_public,
                    'cs2_app_changenumber': loc.notifs_build_cs2_client,
                    'cs2_server_changenumber': loc.notifs_build_cs2_server,
                    'backup_branch_created': loc.notifs_backup_branch_created,
                    'backup_branch_created_sync': f'{loc.notifs_backup_branch_created} 🔃',
                    'backup_branch_updated': loc.notifs_backup_branch_updated,
                    'backup_branch_updated_sync': f'{loc.notifs_backup_branch_created} 🔃',
                    'backup_branch_deleted': loc.notifs_backup_branch_deleted,
                    'misc_branch_created': loc.notifs_misc_branch_created,
                    'misc_branch_updated': loc.notifs_misc_branch_updated,
                    'branch_deleted': loc.notifs_branch_deleted}
MAIN_BRANCHES = {'public', '<null>'}  # <null> is for other important things

MISFIRE_GRACE_TIME = 10

setup_logging(config.LOGS_CONFIG_FILE_PATH)
logger = get_logger(f'{config.NAME}.gc')

shutdown_event = asyncio.Event()
exit_code = 0
background_tasks: set[asyncio.Task] = set()


def _task_done(task: asyncio.Task):
    background_tasks.discard(task)
    if not task.cancelled() and task.exception():
        logger.error('Background task failed', exc_info=task.exception())


def spawn(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    background_tasks.add(task)
    task.add_done_callback(_task_done)
    return task


class PatchedSteamClient(SteamClient):
    """Fixes an infinite program blocking when unable to connect to CM."""

    def _pre_login(self):
        if self.logged_on:
            raise RuntimeError("Already logged on")

        if not self.connected and not self._connecting:
            if not self.connect(retry=10):  # the only change made compared to parent
                return EResult.Fail

        if not self.channel_secured:
            resp = self.wait_event(self.EVENT_CHANNEL_SECURED, timeout=10)

            # some CMs will not send hello
            if resp is None:
                if self.connected:
                    self.wait_event(self.EVENT_DISCONNECTED)
                return EResult.TryAnotherCM

        return EResult.OK


bot = Client(config.BOT_GC_MODULE_NAME,
             api_id=config.API_ID,
             api_hash=config.API_HASH,
             bot_token=config.BOT_TOKEN,
             test_mode=config.TEST_MODE,
             no_updates=True,
             workdir=config.SESS_FOLDER)
client = PatchedSteamClient()
client.set_credential_location(config.STEAM_CREDS_PATH)
cs = CSGOClient(client)
gevent_scheduler = GeventScheduler()
async_scheduler = AsyncIOScheduler()


def is_backup_branch(name: str) -> bool:
    return name.startswith('1.4') or name.startswith('1.3')


@client.on(SteamClient.EVENT_ERROR)
def handle_error(result):
    logger.error(f'Logon result: {result!r}')


@client.on(SteamClient.EVENT_CHANNEL_SECURED)
def send_relogin():
    logger.debug(f'"{SteamClient.EVENT_CHANNEL_SECURED}" event triggered...')
    if client.relogin_available:
        result = client.relogin()
        if result == EResult.OK:
            logger.debug('Re-logged in successfully.')
        else:
            logger.error(f"Failed to re-login: {result!r}")


@client.on(SteamClient.EVENT_CONNECTED)
def log_connect():
    logger.info(f'Connected to {client.current_server_addr}')


@client.on(SteamClient.EVENT_RECONNECT)
def handle_reconnect(delay):
    logger.info(f'Reconnecting in {delay}s...')


@client.on(SteamClient.EVENT_DISCONNECTED)
def handle_disconnect():
    if shutdown_event.is_set():
        return

    logger.warning('Disconnected. Reconnecting...')
    if not client.reconnect(maxdelay=30):
        logger.warning('Failed to reconnect, shutting down the script.')
        request_shutdown(1)
        return
    logger.info('Reconnected successfully.')


@client.on(SteamClient.EVENT_LOGGED_ON)
def handle_after_logon():
    cs.launch()
    if not async_scheduler.running:
        async_scheduler.start()
    if not gevent_scheduler.running:
        gevent_scheduler.start()


@cs.on(CSGOClient.EVENT_READY)
def cs_launched():
    logger.info('CS launched.')


@cs.on(CSGOClient.EVENT_CONNECTION_STATUS)
def update_gc_status(status):
    statuses = {0: States.NORMAL, 1: States.INTERNAL_SERVER_ERROR, 2: States.OFFLINE,
                3: States.RELOADING, 4: States.INTERNAL_STEAM_ERROR}
    game_coordinator_state = statuses.get(status, States.UNKNOWN).literal

    caching.dump_cache_changes(config.GC_CACHE_FILE_PATH, {'game_coordinator_state': game_coordinator_state})

    logger.info(f'Successfully dumped game coordinator status: {game_coordinator_state}')

@async_scheduler.scheduled_job('interval', seconds=45, misfire_grace_time=MISFIRE_GRACE_TIME, max_instances=1)
async def update_depots():
    # noinspection PyBroadException
    try:
        response = client.get_product_info(apps=[730, 2275500, 2275530], timeout=15)
        if not response:
            logger.error(f'Failed to fetch depots, get_product_info() returned {response!r}')
            return
        data = response['apps']

        current_branches = data[730]['depots']['branches']
        cs2_app_change_number = data[2275500]['_change_number']
        cs2_server_change_number = data[2275530]['_change_number']
    except Exception:
        logger.exception('Caught an exception while trying to fetch depots!')
        return
    except gevent.Timeout:  # no idea how to solve it so just shutdown and restart the entire thing somewhere else
        logger.exception('Caught gevent.Timeout, we\'re going to shutdown...')
        request_shutdown(1)
        return

    cache = caching.load_cache(config.GC_CACHE_FILE_PATH)

    new_data = {
        'cs2_app_changenumber': cs2_app_change_number,
        'cs2_server_changenumber': cs2_server_change_number,
        'branches': current_branches
    }

    caching.dump_cache_changes(config.GC_CACHE_FILE_PATH, new_data)

    # noinspection PyBroadException
    try:
        for key, new_value in new_data.items():
            old_value = cache.get(key)
            if old_value is None or old_value == new_value:
                continue

            if key == 'branches':
                await check_for_new_branches(cache, old_value, new_value)
                await check_for_removed_branches(old_value, new_value)
                await check_for_branches_updates(cache, old_value, new_value)
            else:
                # I am an idiot but oh well
                await send_branch_alert('<null>', key, new_value)
    except Exception:
        logger.exception('Caught an exception while trying to fetch depots!')
        return

    caching.dump_cache_changes(config.GC_CACHE_FILE_PATH, new_data)

    logger.info('Successfully dumped game version data.')


async def check_for_new_branches(cache: dict, cached_branches: dict, current_branches: dict):
    cs2_patch_version = cache.get('cs2_patch_version')

    new_branches = current_branches.keys() - cached_branches.keys()
    if not new_branches:
        return

    for branch_name in new_branches:
        branch_data = current_branches[branch_name]
        new_buildid = branch_data.get('buildid')
        if new_buildid is None:
            logger.warning(f'Branch {branch_name} has no buildid!')
            continue

        if is_backup_branch(branch_name):
            event = 'backup_branch_created_sync' if branch_name == cs2_patch_version else 'backup_branch_created'
        else:
            event = 'misc_branch_created'
        await send_branch_alert(branch_name, event, new_buildid)


async def check_for_removed_branches(cached_branches: dict, current_branches: dict):
    removed_branches = cached_branches.keys() - current_branches.keys()
    if not removed_branches:
        return

    for branch_name in removed_branches:
        if is_backup_branch(branch_name):
            event = 'backup_branch_deleted'
        else:
            event = 'branch_deleted'
        await send_branch_alert(branch_name, event)


async def check_for_branches_updates(cache: dict, cached_branches: dict, current_branches: dict):
    cs2_patch_version = cache.get('cs2_patch_version')

    for branch_name, branch_data in current_branches.items():
        cached_branch_data = cached_branches.get(branch_name)

        if cached_branch_data is None:  # newly created, ignore
            continue
        old_buildid = cached_branch_data.get('buildid')
        new_buildid = branch_data.get('buildid')
        if new_buildid is None:
            logger.warning(f'Branch {branch_name} has no buildid!')
            continue
        if old_buildid == new_buildid:
            continue

        if branch_name == 'public':
            spawn(handle_public_branch_update(cache.get('cs2_client_version'), new_buildid))
            continue
        elif is_backup_branch(branch_name):
            event = 'backup_branch_updated_sync' if branch_name == cs2_patch_version else 'backup_branch_updated'
        else:
            event = 'misc_branch_updated'
        await send_branch_alert(branch_name, event, new_buildid)


async def handle_public_branch_update(client_version: int | None, new_buildid: str | None):
    game_version_data = await get_game_version_loop(client_version)
    caching.dump_cache_changes(config.GC_CACHE_FILE_PATH, game_version_data.asdict())
    await send_branch_alert('public', 'public_branch_updated', new_buildid)


async def get_game_version_loop(cached_client_version: int | None, timeout: int = 30 * 60) -> GameVersionData:
    while True:
        deadline = time.monotonic() + timeout
        async with httpx.AsyncClient() as session:
            while time.monotonic() < deadline:
                data = await get_game_version(session, cached_client_version)
                if data:
                    return data
                logger.warning('Failed to pull the game version data, retry in 45 seconds...')
                await asyncio.sleep(45)
        # xPaw: Zzz...
        logger.warning('Reached a timeout while trying to pull the game version data, retry in an hour...')
        await asyncio.sleep(60 * 60)


async def get_game_version(session: httpx.AsyncClient, cached_client_version: int | None) -> GameVersionData | None:
    # noinspection PyBroadException
    try:
        data = await GameVersion.request(session)

        if cached_client_version is None:  # *somehow* don't have anything cached
            logger.info('Successfully pulled the game version data.')
            return data

        # Ensure that the data is up-to-date, so we check datetime
        new_data_datetime = (dt.datetime.fromtimestamp(data.cs2_version_timestamp)
                             .replace(tzinfo=VALVE_TIMEZONE).astimezone(dt.UTC))
        is_up_to_date = (utime.utcnow() - new_data_datetime < dt.timedelta(hours=12))

        if is_up_to_date and data.cs2_client_version != cached_client_version:
            logger.info('Successfully pulled the game version data.')
            return data
    except Exception:
        logger.exception('Caught an exception while trying to get new version!')


@gevent_scheduler.scheduled_job('interval', seconds=45, misfire_grace_time=MISFIRE_GRACE_TIME)
def online_players():
    player_count = client.get_player_count(730)

    if isinstance(player_count, EResult):
        logger.error(f'Failed to fetch player count, got {player_count!r}')
        return

    caching.dump_cache_changes(config.GC_CACHE_FILE_PATH, {'online_players': player_count})

    logger.info(f'Successfully dumped player count: {player_count}')


async def send_branch_alert(branch: str, event: str, new_buildid: str = None):
    logger.info(f'Detected {branch} branch "{event}" event, sending alert...')

    alert_sample = AVAILABLE_ALERTS.get(event)

    if alert_sample is None:
        logger.warning(f'Got wrong event name to send alert: {event}')
        return

    if branch in MAIN_BRANCHES:
        text = alert_sample.format(new_buildid)
    else:
        text = alert_sample.format(branch, new_buildid)

    await send_text_alert(text)


async def send_text_alert(text: str):
    for chat_id in config.CHAT_LIST:
        # noinspection PyBroadException
        try:
            msg = await bot.send_message(chat_id, text, link_preview_options=LinkPreviewOptions(is_disabled=True))
            if chat_id == config.INCS2CHAT:
                await msg.pin(disable_notification=True)
        except Exception:
            logger.exception('Failed to send alert!')


def request_shutdown(code: int = 0):
    global exit_code
    exit_code = max(exit_code, code)
    shutdown_event.set()


async def mainloop():
    from signal import signal as signal_fn, Signals, SIGINT, SIGTERM, SIGABRT

    loop = asyncio.get_running_loop()

    def on_signal(_sig: Signals):
        logger.info(f'Stop signal received ({_sig.name}). Exiting...')
        request_shutdown(0)

    def win_signal_handler(_loop):
        def handler(signum, _frame):
            try:
                _loop.call_soon_threadsafe(on_signal, Signals(signum))
            except RuntimeError:  # loop already closed
                pass
        return handler

    for sig in (SIGINT, SIGTERM, SIGABRT):
        try:
            loop.add_signal_handler(sig, on_signal, sig)
        except NotImplementedError:  # windows
            signal_fn(sig, win_signal_handler(loop))

    await shutdown_event.wait()


async def terminate_all_connections():
    for name, step in (('async scheduler', lambda: async_scheduler.shutdown(wait=False) if async_scheduler.running else None),
                       ('gevent scheduler', lambda: gevent_scheduler.shutdown(wait=False) if gevent_scheduler.running else None),
                       ('cs', cs.exit),
                       ('steam', lambda: client.logout() if client.connected else None)):
        # noinspection PyBroadException
        try:
            step()
        except Exception:
            logger.exception(f'Failed to stop {name}')

    # noinspection PyBroadException
    try:
        if bot.is_connected:
            await bot.stop()
    except Exception:
        logger.exception('Failed to stop bot')
    logger.info('Terminated.')


async def main():
    logger.info('Started.')
    try:
        logger.info('Logging in...')
        result = client.login(username=config.STEAM_USERNAME, password=config.STEAM_PASS)

        if result != EResult.OK:
            logger.error(f"Failed to login: {result!r}")
            request_shutdown(1)
            return

        logger.info('Logged in successfully.')
        await bot.start()
        await mainloop()
    finally:
        await terminate_all_connections()


if __name__ == '__main__':
    # why not `asyncio.run`? short answer: https://pastebin.com/qTECqGwq
    asyncio.get_event_loop().run_until_complete(main())
    sys.exit(exit_code)
