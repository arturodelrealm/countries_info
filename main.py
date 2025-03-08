from enum import Enum

import streamlit as st
import pandas as pd
import numpy as np
import json

COUNTRIES_DATASET_PATH = 'data/consolidated/countries_dataset.csv'
SEP = ';'


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


def display_map(country_information):
    coordinates = country_information.geo_points.values[0]
    if not coordinates:
        return
    country_coordinates = pd.DataFrame(
        json.loads(coordinates), columns=['lon', 'lat'],
    )

    # Display country on map
    st.map(country_coordinates, size=1)


def display_flag(country_information):
    st.image(
        country_information.flag_url.values[0],
        use_container_width=False,
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


data_load_state = st.text('Cargando datos...')
data = load_dataset()
data_load_state.empty()

country_code_to_name = dict(zip(data['code'], data['name']))

# Initialize session state for country and table data
if "country" not in st.session_state:
    st.session_state.country = None


option = st.selectbox(
    '¿Como quieres obtener el país?',
    list(SelectCountryOption),
    format_func=lambda x: x.value
)

if option == SelectCountryOption.SELECTION:
    country = st.selectbox(
        'Selecciona un país:',
        sorted(country_code_to_name),  # Sort by the value instead
        index=None,
        format_func=lambda x: country_code_to_name.get(x, x),
        placeholder='Selecciona un país'
    )
    if country is not None:
        st.session_state.country = country
else:
    text = ''
    if st.button("Obtén un país"):
        st.session_state.country = get_random_country(
            option == SelectCountryOption.BY_POPULATION
        )

# Display selected country
if st.session_state.country:
    st.session_state.selected_country_data = data[
        data.code == st.session_state.country
    ]

    display_country()
