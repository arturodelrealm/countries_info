import gettext

# Define available languages
LANGUAGES = {
    'es': 'Español',
    'en': 'English',
}

# Default language
DEFAULT_LANG = 'es'
LOCALEDIR = 'locales'


def get_translation(lang_code=DEFAULT_LANG):
    """
    Loads the gettext translation for the given language.
    Falls back to default language if not found.
    """
    try:
        lang_translation = gettext.translation(
            'messages', LOCALEDIR, languages=[lang_code])
        lang_translation.install()
        return lang_translation.gettext
    except FileNotFoundError:
        return lambda x: x
    

def format_number(value: float, language: str, max_decimals=None) -> str:
    """
    Formats a number with thousand separators and only shows decimals if 
    they exist.

    :param value: The number to format.
    :param language: The language code (e.g., 'en', 'es').
    :param max_decimals: The number of decimals shown. If not defined show all.
    :return: The formatted number as a string.

    Thanks chatgpt
    """
    default_separator = ('.', ',')
    separators = {
        'en': (',', '.'),  # English: 1,000,000.50
        'es': ('.', ','),  # Spanish: 1.000.000,50 
    }

    thousand_sep, decimal_sep = separators.get(language[:2], default_separator)

    # Format number with thousand separator
    integer_part, decimal_part = f'{value:,.20f}'.rstrip('0').split('.')

    # If there are no decimals left, don't add the decimal separator
    formatted_number = integer_part.replace(",", thousand_sep)
    if decimal_part:  # Only add decimals if they exist
        if max_decimals:
            decimal_part = decimal_part[:max_decimals]
        formatted_number += decimal_sep + decimal_part

    return formatted_number
