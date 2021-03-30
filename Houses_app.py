# Import necessary libraries
import pandas as pd
import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
from datetime import datetime

# Expand layout page
st.set_page_config(layout='wide')

# O recurso @st.cahe() permite que o amarzenar os dados em mémoria cache e agilizar a visualizalção dos dados 
@st.cache(allow_output_mutation = True)

# Definindo uma função para ler o arquivo CSV
def add_data(path):
    data = pd.read_csv(path)

    return data

# Add data path
path = 'kc_house_data.csv'
data = add_data(path)

# Overview attributes
st.title('Houses Business Analyse App')

st.title('Overview attributes')

# Aqui usando st.write() podemos adacionar textos como comentários dentro aplicativo
st.write("*We can select the columns that we wish using the sidebar selectors and control the dataset overview.")
st.write("*The panel 'Describe Statistics Attributes' show the main statistics of the numerical attributes into the dataset.")
st.write(" *The 'Main Attributes' show some attributes that we choose like main for analyse.")

# Podemos usar o comando st.header() para destacar algumas atribuições textuais
st.header('Dataset Overview')

st.sidebar.title('Costume overview')

# O comando st.sidebar.multiselect( ) nos permite adicionarmos uma barra de seleção na lateral da tela de exibição do aplicativo
# Essas barras de seleção em específico permite que possamos escoler as colunas do dataset que serão exibidas e o zipcode

fe_attributes = st.sidebar.multiselect('Choose your columns in dataset overview', data.columns)
fe_zipcode = st.sidebar.multiselect('Choose your zipcode in dataset overview', data['zipcode'].unique())

# Para que o recurso sidebar seja funcional temos que garantir que o dataset exiba apenas os valores selecionados pelos nossos filtros. 
# Para isso usamos o comando .isin( ) e além disso queremos que mater a visualização se caso nenhum filtro for selecionado, por isso usamos os condições para cria um default
if (fe_zipcode != []) & (fe_attributes != []):
    df = data.loc[data['zipcode'].isin(fe_zipcode), fe_attributes]

elif (fe_zipcode != []) & (fe_attributes == []):
    df = data.loc[data['zipcode'].isin(fe_zipcode), :]

elif (fe_zipcode == []) & (fe_attributes != []):
    df = data.loc[:, fe_attributes]

else:
    df = data.copy()

# Com o comando st.beta_columns( )  podemos controlar a posição das visualizações dos dados na tela 
c1, c2 = st.beta_columns((1, 1))

c1.dataframe(df)

# Podemos escoler algumas colunas que julgamos ser mais importantes e filtra-las por zipcode usando o comando .groupby().
# Isso permite apllicar uma análise estatistica sobre cada essas colunas em termos de cada zipcode que desejarmos.
# Por exemplo em 'da2' agrupamos todos os preços médios contidos em cada zipcode da cidade
da1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
da2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
da3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()

# Usando o comando .merge( ) garantimos que estamos unindo todos os objetos pelo seu atributo em comunm, o seu zipcode
m1 = pd.merge(da1, da2, on = 'zipcode', how ='inner')
da = pd.merge(m1, da3, on = 'zipcode', how ='inner')

da.columns = ['Zipcode', ' Total Houses', 'Price', 'Sqft Living']

c1.header("Main Attributes")

c1.dataframe(da, height=400)

# É interessante criarmos uma uma visualização que mostra algumas informações estátisticas das nossas colunas
# Com o comando select_dtypes( ) selecionamos apenas as colunas com valores númericos 
# Em seguida aplicamos o valores estátiscos que quermos extrair com o comando .apply( )
n_attributes = data.select_dtypes(include=['int64', 'float64'])
square = pd.DataFrame(n_attributes.apply(np.std))
mean_ = pd.DataFrame(n_attributes.apply(np.mean))
median_ = pd.DataFrame(n_attributes.apply(np.median))
max_ = pd.DataFrame(n_attributes.apply(np.max))
min_ = pd.DataFrame(n_attributes.apply(np.min))

# Aqui podemos usar apenas o .concat() para unir dos os objetos, já que eles não tem atributos em comum
df1 = pd.concat([square, mean_, median_, max_, min_], axis = 1).reset_index()

df1.columns = ['Attributes', 'Square', 'Mean', 'Median', 'Max', 'Min']

c2.header("Describe Statistics Attributes")

c2.dataframe(df1, height = 400)

# Houses density
# Nesse parte queremos desenhar um mapa que mostre a distribuição das casas pela cidade. 
# Esse é um recurso muito importante para que possamos ter um panorama geral da localização e facilite a avaliação de valor dos imóveis
st.title("Region Overview")
st.write("The map 'Houses Density' show the houses density distributions and some its features like 'price', 'area', year of built ... ")


c1, c2 = st.beta_columns((1, 1))
c1.header("Houses Density")

# A biblioteca folium criar os mapas que queremos plotar com o comando .Map( ) 
# Basta fornecermos as coordenas das casas que se encontram nas colunas 'lat' e 'long'
density_map = folium.Map( 
    location=[data['lat'].mean(), data['long'].mean()], default_zoom_start=15
)

# Aqui selecionamos uma amostra dos dados que queremos exibir no mapa
sam = data.sample(1000)

# Com a classe MakerCluster() é posível adicionarmos alguns marcadores que fornecem informações na tela ao usuario sobre cada imóveis que selecionarmos
cluster = MarkerCluster().add_to(density_map)
for name, row in sam.iterrows():
    folium.Marker([row['lat'], row['long']],
     popup='Sold S$ on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(row['price'],
     row['date'], row['sqft_living'], row['bedrooms'], row['bathrooms'], row['yr_built'])).add_to(cluster)

with c1:
    folium_static(density_map)

st.sidebar.title('Commercial options')
st.title('Commercial attributes')

st.write("In this section, we can control the price view as a function of time using two filters 'Select Max Date' and 'Select Max Year Built'.")

# The average price per day
# Outra informação muito valiosa que gostários da ter é como preço dos imóveis varia com o tempo.
# Com esssa finalidade criamos dois filtros, um que permite escolhermos uma data específica e outro que permite escolher apenas os anos,
# desse modo podemos ver o gráfico da varaição do preço 
st.header('Avarage Price per day')
st.sidebar.subheader('Select Max Date')
 
data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d') # Converting data['date'] to date time type

# filters
# Aqui precisamos coverter os valores data['date'] que são do tipo string em tipo data para que os filtros sejam funcionais
# Usamos para isso a biblioteca datatime  e o comando .strptime( ) para fazer a conversão para tipo data
min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')

# Criando o sidebar que vai permiter selecionarmos a data desejada
f_date = st.sidebar.slider(' Select Date', min_date, max_date, min_date)

# Precissamos garantir que as comparações que os códigos farão entre os dados dentros dos filtros sejam do mesmo tipo
# Logo com o comando .to_datetime()  as comparações serão do tipo certo.
data['date'] = pd.to_datetime(data['date'])

# Filtrando os dados que serão exibidos no gráfico
df = data.loc[data['date'] < f_date]
df = df[['date', 'price']].groupby('date').mean().reset_index()

fig = px.line(df, x = 'date', y = 'price')
st.plotly_chart(fig, use_container_width=True)

# The average price per year

# filters
min_year_built = int(data['yr_built'].min())
max_year_built = int(data['yr_built'].max())

# Criando o sidebar que vai permiter selecionarmoso ano desejado
st.sidebar.subheader('Select Max Year Built')
f_year_built = st.sidebar.slider( 'Year Built', min_year_built,
                                                max_year_built,
                                                min_year_built )
st.header('The average price per year built')    

# Filtrando os dados que serão exibidos no gráfico
df = data.loc[data['yr_built'] < f_year_built ]
df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

fig = px.line(df, x = 'yr_built', y = 'price')
st.plotly_chart(fig, use_container_width=True)

# Statistic Plots
# Nessa última parte construimos gráficos que possam dar outras informações gerais, 
#claro que dependendo da necessidade do cliente gráficos diferentes podem ser emplementados
st.header('Price Distribution')

# Esse o sidebar que vai permite contolarmos a distribuição dos preços das casas
st.sidebar.subheader('Select Max Price')
st.write("Using 'Select Max Price' filter we can control price count distribution. ")

price_min = int(data['price'].min())
price_max = int(data['price'].max())
price_avg = int(data['price'].mean())

f_price = st.sidebar.slider('Price', price_min, price_max, price_avg)
df = data.loc[data['price']< f_price]

# Houses price distributions
fig = px.histogram(df, x = 'price', nbins=50)
st.plotly_chart(fig, use_container_width= True)

# Houses Distributions
st.sidebar.title('Another Attibutes')
st.title('Houses Another Attibutes')

st.write("With the filters 'Max number of bedrooms' and 'Max number of bathrooms' we control de view of count houses with those attributes.")
# filters
fe_bedrooms = st.sidebar.selectbox('Max number of bedrooms', sorted(set(data['bedrooms'].unique())))
fe_bathrooms = st.sidebar.selectbox('Max number of bathrooms', sorted(set(data['bathrooms'].unique())))

c1, c2 = st.beta_columns(2)

# Houses per  bedrooms
c1.header('Houses per  bedrooms')
df = data[data['bedrooms'] < fe_bedrooms]
fig = px.histogram(df, x = 'bedrooms', nbins = 19)
c1.plotly_chart(fig, use_container_width= True)

# Houses per bathrooms
c2.header('Houses per  bathrooms')
df = data[data['bathrooms'] < fe_bathrooms]
fig = px.histogram(df, x = 'bathrooms', nbins = 19)
c2.plotly_chart(fig, use_container_width= True)

st.write(" The filters 'Max number of floors' and 'Houses with waterview' select the houses with desired number floors and the second select houses with water view.")
# filters
fe_floors = st.sidebar.selectbox('Max number of floors', sorted(set(data['floors'].unique())))
fe_waterview = st.sidebar.checkbox('Houses with waterview')

c1, c2 = st.beta_columns(2)

# Houses per floors
c1.header('Houses per floors')
df = data[data['floors'] < fe_floors]

fig = px.histogram(data, x = 'floors', nbins = 19)
c1.plotly_chart(fig, use_container_width= True)

# Houses per waterview
if fe_waterview:
    df = data[data['waterfront'] == 1]

else:
    df = data.copy()

fig = px.histogram(df, x = 'waterfront', nbins=10)
c2.plotly_chart(fig, use_container_width= True)

