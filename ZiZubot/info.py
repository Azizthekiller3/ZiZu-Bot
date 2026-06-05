import re
import os
from os import environ
from Script import script

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

def _require_int(name, default=None):
    """Read an env var as int; crash with a clear message if missing/invalid."""
    val = environ.get(name, '')
    if not val:
        if default is not None:
            return default
        raise EnvironmentError(f"Required env var '{name}' is not set. Add it to your environment variables.")
    try:
        return int(val)
    except ValueError:
        raise EnvironmentError(f"Env var '{name}' must be an integer, got: '{val}'")

def _require_str(name):
    """Read a required string env var; crash with a clear message if missing."""
    val = environ.get(name, '')
    if not val:
        raise EnvironmentError(f"Required env var '{name}' is not set. Add it to your environment variables.")
    return val

# Bot information
SESSION = environ.get('SESSION', 'ZiZuBot_Session')
# FIX: give clear error messages when required env vars are missing
API_ID = _require_int('API_ID')
API_HASH = _require_str('API_HASH')
BOT_TOKEN = _require_str('BOT_TOKEN')

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', 'False'), False)
_default_pic = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'zizubot_logo.jpg')
PICS = environ.get('PICS', _default_pic).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = environ.get('AUTH_CHANNEL')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = _require_str('DATABASE_URI')
DATABASE_NAME = environ.get('DATABASE_NAME', "ZiZuBot")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# Others
LOG_CHANNEL = _require_int('LOG_CHANNEL')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'ZiZuBot_support')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', 'True')), False)
IMDB = is_enabled((environ.get('IMDB', 'False')), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', 'True')), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CUSTOM_FILE_CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", "📂 <em>File Name</em>: <code>{file_name}</code>\n\n ♻ <em>File Size</em>:{file_size} \n\n <b><i>ZiZuBot — Your Smart Auto Filter Assistant</i></b>")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "🏷 𝖳𝗂𝗍𝗅𝖾: <a href={url}>{title}</a> \n🔮 𝖸𝖾𝖺𝗋: {year} \n⭐️ 𝖱𝖺𝗍𝗂𝗇𝗀𝗌: {rating}/ 10 \n🎭 𝖦𝖾𝗇𝗋𝖾𝗌: {genres} \n\n🎊 𝖯𝗈𝗐𝖾𝗋𝖾𝖽 𝖡𝗒 ZiZuBot™")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = _require_int('INDEX_REQ_CHANNEL', default=LOG_CHANNEL)
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "False")), True)

LOG_STR = "Current Customized Configurations for ZiZuBot:\n"
LOG_STR += ("IMDB Results are enabled.\n" if IMDB else "IMDB Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found, Users will be redirected to bot PM.\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF disabled.\n")
LOG_STR += ("SINGLE_BUTTON is Found.\n" if SINGLE_BUTTON else "SINGLE_BUTTON disabled.\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION disabled.\n")
LOG_STR += ("Spell Check Mode Is Enabled.\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled.\n")
LOG_STR += (f"MAX_LIST_ELM Found: {MAX_LIST_ELM}\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown.\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
