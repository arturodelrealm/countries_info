from enum import Enum

import streamlit as st
import pandas as pd
import numpy as np
import json

from i18n import get_translation, DEFAULT_LANG, LANGUAGES, format_number


COUNTRIES_DATASET_PATH = 'data/consolidated/countries_dataset.csv'
CONTINENTS_DATASET_PATH = 'data/consolidated/continents.csv'
SEP = ';'
FLAG_NOT_FOUND_URL = 'https://upload.wikimedia.org/wikipedia/commons/2/2f/' \
    'Missing_flag.png'


def set_language():
    """Set language and get the corresponding translator"""
    if 'language' not in st.session_state:
        st.session_state.language = DEFAULT_LANG

    translator = get_translation(st.session_state.language)
    language = st.sidebar.selectbox(
        translator('Selecciona un idioma'),
        LANGUAGES,
        format_func=lambda x: LANGUAGES[x],
    )
    if language != st.session_state.language:
        st.session_state.language = language
        translator = get_translation(st.session_state.language)
    return translator


st.set_page_config(
    page_title='Donde nací',
    page_icon=':world_map:',
    initial_sidebar_state='collapsed',
)

_ = set_language()


class SelectCountryOption(Enum):
    BY_POPULATION = _('Por población')
    RANDOM = _('Aleatorio')
    SELECTION = _('Seleccionar uno manualmente')


@st.cache_data
def load_dataset():
    dataset = pd.read_csv(COUNTRIES_DATASET_PATH, sep=SEP)
    dataset = dataset[dataset['population'].notna()]
    return dataset


@st.cache_data
def load_continents_data():
    return pd.read_csv(CONTINENTS_DATASET_PATH, sep=SEP)


def get_random_country(using_distribution=True):
    if using_distribution:
        distribution = data['population'] / data['population'].sum()
    else:
        distribution = None
    return np.random.choice(data['code'], p=distribution)


def select_country(code_to_name):
    option = st.selectbox(
        _('¿Como quieres obtener el país?'),
        list(SelectCountryOption),
        format_func=lambda x: x.value
    )
    country = None
    if option == SelectCountryOption.SELECTION:
        country = st.selectbox(
            _('Selecciona un país:'),
            sorted(
                country_code_to_name,
                key=lambda x: code_to_name.get(x, x)
            ),
            index=None,
            format_func=lambda x: code_to_name.get(x, x),
            placeholder=_('Selecciona un país')
        )

    else:
        if st.button(_('¿Dónde nací?')):
            country = get_random_country(
                option == SelectCountryOption.BY_POPULATION
            )
    if country is not None:
        st.session_state.country = country
    return country


def display_map(country_information):
    coordinates = country_information.geo_points.values[0]
    if not coordinates:
        return
    country_coordinates = pd.DataFrame(
        json.loads(coordinates), columns=['lon', 'lat'],
    )

    # Display country on map with a discrete color
    st.map(country_coordinates, color='#eeeeee')


def display_flag(country_information):
    flag_url = country_information.flag_url.values[0]
    caption = None
    if not isinstance(flag_url, str) and np.isnan(flag_url):
        flag_url = FLAG_NOT_FOUND_URL
        caption = _('Bandera no encontrada')
    st.image(
        flag_url,
        use_container_width=False,
        caption=caption,
    )


def display_country_information(information, continent_name_map):
    language = st.session_state.language
    if not np.isnan(information.life_expectancy.values[0]):
        life_expectancy = format_number(
            information.life_expectancy.values[0],
            language,
            2
        )
    else:
        life_expectancy = '????'

    if not np.isnan(information.infant_mortality.values[0]):
        infant_mortality = format_number(
            information.infant_mortality.values[0] / 10,
            language,
            2
        ) + '%'
    else:
        infant_mortality = _('No hay información')
    continent_code = information.continent.values[0]
    continent_name = continent_name_map[continent_code]
    values_to_display = [
        (_('Capital'), information.capital.values[0]),
        (_('Continente'), continent_name),
        (
            _('Población'),
            format_number(
                information.population.values[0],
                language
            )
        ),
        (
            _('Área (km^2)'),
            format_number(
                information.area.values[0],
                language
            )
        ),
        (_('Expectativa de vida'), _('{} años').format(life_expectancy)),
        (_('Probabilidad de no superar el año'), infant_mortality),
        (
            _('Más información del país en'),
            get_wikipedia_link(
                information[f'name_{language}'].values[0],
                language
            )
        ),
    ]
    for title, value in values_to_display:
        st.write(f'**{title}:** {value}')


def display_country(continent_name_map):
    if 'selected_country_data' in st.session_state:
        information = st.session_state.selected_country_data
    else:
        return

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        st.title(
            _("País seleccionado: {}").format(
                information[f'name_{st.session_state.language}'].values[0]
            )
        )

    with col2:
        display_flag(information)

    display_map(information)

    display_country_information(information, continent_name_map)


def get_wikipedia_link(country_name, language='es'):
    country_name_formatted = country_name.replace(" ", "_")
    return f"https://{language}.wikipedia.org/wiki/{country_name_formatted}"


st.title(_('¿Dónde podría haber nacido?'))

with st.spinner(_('Cargando datos...')):
    data = load_dataset()
    continents_data = load_continents_data()

country_code_to_name = dict(
    zip(
        data['code'],
        data[f'name_{st.session_state.language}']
    )
)

continent_code_to_name = dict(
    zip(
        continents_data['code'],
        continents_data[f'name_{st.session_state.language}']
    )
)

# Initialize session state for country
if "country" not in st.session_state:
    st.session_state.country = None

select_country(country_code_to_name)

# Display selected country
if st.session_state.country:
    st.session_state.selected_country_data = data[
        data.code == st.session_state.country
    ]

    display_country(continent_code_to_name)
