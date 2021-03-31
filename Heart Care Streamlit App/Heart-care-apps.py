# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier

# O comando abaixo permite que as janelas exibidas ocupem maior espaço em tela.
st.set_page_config(layout='wide')

# Aqui escrevemos uma pequena descrição da funcionalidade do aplicativo
st.write("""
# Heart sick Prediction App

The app predicts if someone has any type of heart disease based on some indicators

""")

st.sidebar.header('User Input Features')


st.sidebar.markdown("""
[Example CSV input file](https://raw.githubusercontent.com/RondinellyMorais/heart_health/main/df_exemple.csv)
""")

# No trecho de código abaixo construimos todos os seletores de barra e de caixa nessários para inserir todas as features
# Collects user input features into dataframe
uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
else:
    def user_input_features():  
        cholesterol = st.sidebar.selectbox('Cholesterol Level',('1','2','3'))
        gluc = st.sidebar.selectbox('Gluc Level',('1','2','3'))
        gender = st.sidebar.selectbox('0: Famale, 1: Male',('0''1'))
        smoke = st.sidebar.selectbox(' 0: No Smoke, 1: Smoke',('0','1'))
        alco =  st.sidebar.selectbox('Alcohol Consumer, 0: no, 1: yes',('0','1'))
        active = st.sidebar.selectbox('Physical Activity, 0: no, 1: yes',('0','1'))
        age= st.sidebar.slider('Age in Days', 10798, 23713, 15000)
        height = st.sidebar.slider('Height: cm', 55, 250, 100)
        weight = st.sidebar.slider('Weight: Kg', 10.0, 200.0, 100.0)
        ap_hi = st.sidebar.slider('Ap_hi', 93, 169, 120)
        ap_lo = st.sidebar.slider('Ap_lo', 52, 115, 80)
        data = {'cholesterol': cholesterol,
                'gluc': gluc,
                'smoke': smoke,
                'alco': alco,
                'active': active,
                'age': age,
                'height': height,
                'weight': weight,
                'ap_hi': ap_hi,
                'ap_lo': ap_lo,
                'gender': gender}
        features = pd.DataFrame(data, index=[0])
        return features
    input_df = user_input_features()

# Carrendo o arquivo .csv para alimentar o modelo de previsão 
hert = pd.read_csv('heart_app.csv')
herts = hert.drop(columns=['cardio'])
df = pd.concat([input_df, herts],axis=0)

# O código abaixo mostra as features que serão usadas na previsão
df = df[:1]


st.subheader('User Input parameters')

# Esse comando permite que caso o programa não carrego o dataset, possamos adicionar-lo manualmente
if uploaded_file is not None:
    st.write(df)
else:
    st.write('Awaiting CSV file to be uploaded. Currently using example input parameters (shown below).')
    st.write(df)

# Usamos o algoritmo RandomFlorestClassifier e o importamos como um arquivo pickle    
# Reads in saved classification model
load_clf = pickle.load(open('heart_clf.pkl', 'rb'))

# Apply model to make predictions
prediction = load_clf.predict(df)
prediction_proba = load_clf.predict_proba(df)

# Aqui determinamos a acuracia do método
X = hert.drop('cardio', axis= 1)
Y = hert['cardio']
acc = load_clf.score(X, Y)
st.write('Accuracy of method:{:.2f} %'.format(100*acc))

# Classificação da previsão
st.subheader('Prediction ( 0: no sick, 1: sick )')
heart_cardio = np.array([0, 1])
st.write(heart_cardio[prediction])

st.subheader('Prediction Probability')
st.write(100*prediction_proba)

