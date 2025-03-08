from enum import Enum

import streamlit as st
import pandas as pd
import numpy as np
import json

COUNTRIES_DATASET_PATH = 'data/consolidated/countries_dataset.csv'
SEP = ';'
FLAG_NOT_FOUND_URL = 'https://upload.wikimedia.org/wikipedia/commons/2/2f/' \
    'Missing_flag.png'


class SelectCountryOption(Enum):
    BY_POPULATION = 'Por población'
    RANDOM = 'Aleatorio'
    SELECTION = 'Seleccionar uno manualmente'


@st.cache_data
def load_dataset():
    dataset = pd.read_csv(COUNTRIES_DATASET_PATH, sep=SEP)
    dataset = dataset[dataset['population'].notna()]
    return dataset


def big_number_prettifier(number):
    return f'{number:,}'.replace(',', '.')


def get_random_country(using_distribution=True):
    if using_distribution:
        distribution = data['population'] / data['population'].sum()
    else:
        distribution = None
    return np.random.choice(data['code'], p=distribution)


def select_country(code_to_name):
    option = st.selectbox(
        '¿Como quieres obtener el país?',
        list(SelectCountryOption),
        format_func=lambda x: x.value
    )
    country = None
    if option == SelectCountryOption.SELECTION:
        country = st.selectbox(
            'Selecciona un país:',
            sorted(
                country_code_to_name,
                key=lambda x: code_to_name.get(x, x)
            ),
            index=None,
            format_func=lambda x: code_to_name.get(x, x),
            placeholder='Selecciona un país'
        )

    else:
        if st.button("¿Dónde nací?"):
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
        caption = 'Bandera no encontrada'
    st.image(
        flag_url,
        use_container_width=False,
        caption=caption,
    )


def display_country_information(information):
    if not np.isnan(information.life_expectancy.values[0]):
        life_expectancy = f'{information.life_expectancy.values[0]:.2f}'
    else:
        life_expectancy = '????'

    if not np.isnan(information.infant_mortality.values[0]):
        infant_mortality = \
            f'{information.infant_mortality.values[0] / 10:.2f}%'
    else:
        infant_mortality = 'No hay información'

    values_to_display = [
        ('Capital', information.capital.values[0]),
        ('Continente', information.continent.values[0]),
        (
            'Población',
            big_number_prettifier(information.population.values[0])
        ),
        ('Área (km^2)', big_number_prettifier(information.area.values[0])),
        ('Expectativa de vida', f'{life_expectancy} años'),
        ('Probabilidad de no superar el año', infant_mortality),
        (
            'Más información del país en',
            get_wikipedia_link(information.name.values[0])
        ),
    ]
    for title, value in values_to_display:
        st.write(f'**{title}:** {value}')


def display_country():
    if 'selected_country_data' in st.session_state:
        information = st.session_state.selected_country_data
    else:
        return

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        st.title(f"País seleccionado: {information.name.values[0]}")

    with col2:
        display_flag(information)

    display_map(information)

    display_country_information(information)


def get_wikipedia_link(country_name):
    country_name_formatted = country_name.replace(" ", "_")
    return f"https://es.wikipedia.org/wiki/{country_name_formatted}"


st.set_page_config(
    page_title='Donde nací',
    page_icon=':world_map:'
)
st.title('¿Dónde podría haber nacido?')

with st.spinner('Cargando datos...'):
    data = load_dataset()

country_code_to_name = dict(zip(data['code'], data['name']))

# Initialize session state for country
if "country" not in st.session_state:
    st.session_state.country = None

select_country(country_code_to_name)

# Display selected country
if st.session_state.country:
    st.session_state.selected_country_data = data[
        data.code == st.session_state.country
    ]

    display_country()
