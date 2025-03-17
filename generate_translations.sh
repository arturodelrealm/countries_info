#!/bin/bash

# Define language codes
LANGUAGES=("es" "en")

# Extract translatable strings from Python files
xgettext -o locales/messages.pot --language=Python --keyword=_ --from-code=UTF-8 ./*.py

# Initialize translation files if they don’t exist
for LANG in ${LANGUAGES[@]}; do
    mkdir -p locales/$LANG/LC_MESSAGES
    if [ ! -f "locales/$LANG/LC_MESSAGES/messages.po" ]; then
        msginit --locale=$LANG -o "locales/$LANG/LC_MESSAGES/messages.po" -i locales/messages.pot --no-translator
    fi
    msgmerge -U -i "locales/$LANG/LC_MESSAGES/messages.po" locales/messages.pot
done

# Compile translations
for LANG in ${LANGUAGES[@]}; do
    msgfmt -o "locales/$LANG/LC_MESSAGES/messages.mo" "locales/$LANG/LC_MESSAGES/messages.po"
done

echo "✅ Translations updated!"
