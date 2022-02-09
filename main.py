import pandas as pd
import numpy as np
import streamlit as st
import time

colunas = ['ID_Entrada', 'Mchn', 'ID_Funcionario', 'Nome', 'Modo', 'IOMd', 'Data', 'Hora']

meses = {1 : 'Janeiro',
2 : 'Fevereiro',
3 : 'Março',
4 : 'Abril',
5 : 'Maio',
6 : 'Junho',
7 : 'Julho',
8 : 'Agosto',
9 : 'Setembro',
10 : 'Outubro',
11 : 'Novembro',
12 : 'Dezembro'}

def separa_funcionario(df, nome, ano, mes):

    funcionario = df[(df['Nome'] == nome) & (df['Ano'] == ano) & (df['Mes'] == mes)].reset_index()

    return funcionario

def agrupa_dias_trabalhados(df):

  dias_trab = df.groupby(by=['Data'])

  return dias_trab

def calcula_hora(ag):
    df = pd.DataFrame(columns=['index', 'Data_Hora', 'ID_Entrada',
                               'Mchn', 'ID_Funcionario', 'Nome', 'Modo',
                               'IOMd', 'Data', 'Hora', 'Ano', 'Mes', 'Dia',
                               'Horas_Trabalhadas', 'Observacao'])

    for name, data in ag:

        df_temp = pd.DataFrame(ag.get_group(name))

        if len(df_temp) == 4:
            hrs = (df_temp['Data_Hora'].iloc[3] - df_temp['Data_Hora'].iloc[2]) + (
                        df_temp['Data_Hora'].iloc[1] - df_temp['Data_Hora'].iloc[0])
            df_temp['Hora_Entrada'] = df_temp['Data_Hora'].iloc[0]
            df_temp['Hora_Saida_Almoco'] = df_temp['Data_Hora'].iloc[1]
            df_temp['Hora_Volta_Almoco'] = df_temp['Data_Hora'].iloc[2]
            df_temp['Hora_Saida'] = df_temp['Data_Hora'].iloc[3]
            df_temp['Hora_Nao_Identificada'] = pd.NaT
            df_temp['Horas_Trabalhadas'] = hrs
            df_temp['Observacao'] = 'Tudo ok!'

        elif len(df_temp) == 3:
            hrs = df_temp['Data_Hora'].max() - df_temp['Data_Hora'].min() - pd.Timedelta(hours=1, minutes=30)
            df_temp['Hora_Entrada'] = df_temp['Data_Hora'].min()
            df_temp['Hora_Saida_Almoco'] = pd.NaT
            df_temp['Hora_Volta_Almoco'] = pd.NaT
            df_temp['Hora_Saida'] = df_temp['Data_Hora'].max()
            df_temp['Hora_Nao_Identificada'] = df_temp['Data_Hora'].iloc[1]
            df_temp['Horas_Trabalhadas'] = hrs
            df_temp['Observacao'] = 'Neste dia so passou 3 vezes!'

        elif len(df_temp) == 2:
            hrs = df_temp['Data_Hora'].max() - df_temp['Data_Hora'].min()
            df_temp['Hora_Entrada'] = df_temp['Data_Hora'].min()
            df_temp['Hora_Saida_Almoco'] = pd.NaT
            df_temp['Hora_Volta_Almoco'] = pd.NaT
            df_temp['Hora_Saida'] = df_temp['Data_Hora'].max()
            df_temp['Hora_Nao_Identificada'] = pd.NaT
            df_temp['Horas_Trabalhadas'] = hrs
            df_temp['Observacao'] = 'Neste dia so passou 2 vezes!'

        elif len(df_temp) == 1:
            hrs = df_temp['Data_Hora'].max() - df_temp['Data_Hora'].min()
            df_temp['Hora_Entrada'] = pd.NaT
            df_temp['Hora_Saida_Almoco'] = pd.NaT
            df_temp['Hora_Volta_Almoco'] = pd.NaT
            df_temp['Hora_Saida'] = pd.NaT
            df_temp['Hora_Nao_Identificada'] = df_temp['Data_Hora'].min()
            df_temp['Horas_Trabalhadas'] = hrs
            df_temp['Observacao'] = 'Neste dia so passou 1 vez!'

        else:

            if df_temp['Data_Hora'].iloc[1] - df_temp['Data_Hora'].iloc[0] > pd.Timedelta(hours=1, minutes=30):

                hrs = (df_temp['Data_Hora'].iloc[-1] - df_temp['Data_Hora'].iloc[-2]) + (df_temp['Data_Hora'].iloc[1] - df_temp['Data_Hora'].iloc[0])
                df_temp['Hora_Entrada'] = df_temp['Data_Hora'].iloc[0]
                df_temp['Hora_Saida_Almoco'] = df_temp['Data_Hora'].iloc[1]
                df_temp['Hora_Volta_Almoco'] = df_temp['Data_Hora'].iloc[-2]
                df_temp['Hora_Saida'] = df_temp['Data_Hora'].iloc[-1]
                df_temp['Hora_Nao_Identificada'] = df_temp['Data_Hora'].iloc[2]
                df_temp['Horas_Trabalhadas'] = hrs
                df_temp['Observacao'] = 'Neste dia passou mais de 4 vezes!'

            else:

                hrs = (df_temp['Data_Hora'].iloc[-1] - df_temp['Data_Hora'].iloc[-2]) + (df_temp['Data_Hora'].iloc[2] - df_temp['Data_Hora'].iloc[0])
                df_temp['Hora_Entrada'] = df_temp['Data_Hora'].iloc[0]
                df_temp['Hora_Saida_Almoco'] = df_temp['Data_Hora'].iloc[2]
                df_temp['Hora_Volta_Almoco'] = df_temp['Data_Hora'].iloc[-2]
                df_temp['Hora_Saida'] = df_temp['Data_Hora'].iloc[-1]
                df_temp['Hora_Nao_Identificada'] = df_temp['Data_Hora'].iloc[1]
                df_temp['Horas_Trabalhadas'] = hrs
                df_temp['Observacao'] = 'Neste dia passou mais de 4 vezes!'

        df = pd.concat([df, df_temp])

    df.drop_duplicates(subset='Data', inplace=True, ignore_index=True)

    return df

def converte_horas(seg):

  horas = seg // 3600

  resto_horas = seg % 3600

  minutos = resto_horas // 60

  segundos = resto_horas % 60

  return (f'''{horas} hora(s), {minutos} minuto(s), {segundos} segundo(s)''')

def verifica_horas_trabalhadas(df):

    agrupar_ano_mes = df.groupby(['Ano', 'Mes'])

    informacao_horas = []

    for nome, value in agrupar_ano_mes:

        mes = pd.DataFrame(agrupar_ano_mes.get_group(nome))

        informacao_horas.append(converte_horas(pd.Timedelta(mes['Horas_Trabalhadas'].sum()).total_seconds()))

    return informacao_horas

st.set_page_config(page_title = 'Horas Funcionários', layout = 'wide')


def set_page_container_style(max_width: int = 1100, max_width_100_percent: bool = False,
                             padding_top: int = 1, padding_right: int = 2, padding_left: int = 2,
                             padding_bottom: int = 10):
    if max_width_100_percent:
        max_width_str = f'max-width: 100%;'
    else:
        max_width_str = f'max-width: {max_width}px;'

    st.markdown(
        f'''
        <style>
            .reportview-container .sidebar-content {{
                padding-top: {padding_top}rem;
            }}
            .reportview-container .main .block-container {{
                {max_width_str}
                padding-top: {padding_top}rem;
                padding-right: {padding_right}rem;
                padding-left: {padding_left}rem;
                padding-bottom: {padding_bottom}rem;
            }}
        </style>
        ''',
        unsafe_allow_html=True)

set_page_container_style()

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)

col11, col22, col33 = st.columns((1, 2, 1))

col22.title('Horário dos Funcionários')

arquivo = col22.file_uploader('Insira o arquivo de horário dos funcionários', accept_multiple_files=False)

if arquivo:

    horarios = pd.read_table(arquivo, sep='\s+',
                            encoding='utf_16_le', header = 0, names = colunas,
                            parse_dates = [['Data', 'Hora']], keep_date_col = True)

    horarios['Ano'] = horarios['Data_Hora'].dt.year
    horarios['Mes'] = horarios['Data_Hora'].dt.month
    horarios['Dia'] = horarios['Data_Hora'].dt.day

    func = st.sidebar.selectbox('Escolha o funcionário', options = sorted(horarios['Nome'].unique()))

    ano = int(st.sidebar.selectbox('Escolha o Ano', options = [2022, 2021, 2020], index = 1))

    mes = int(st.sidebar.selectbox('Escolha o Mês', options = sorted(horarios['Mes'].unique())))

    if func and ano and mes:

        try:

            col1, col2, col3, col4 = st.columns((2, 1, 2, 1))

            funcionario = separa_funcionario(horarios, func, ano, mes)

            col1.markdown(f'### Os horários de {func}:')
            col1.write(funcionario[['Nome', 'Data', 'Hora']])

            temp0 = funcionario[['Nome', 'Data', 'Hora']]

            col1.download_button(label='Download da Lista de Horas',
                                       data=temp0.to_csv(index=False, na_rep='Nao houve'),
                                       file_name=f'Lista_Horas_{func}.csv')

            temp1 = agrupa_dias_trabalhados(funcionario)

            horas_funcionario = calcula_hora(temp1)

            temp2 = horas_funcionario.astype('str')

            st.markdown(f'### As horas que {func} trabalhou por dia em {meses[mes]}:')

            st.write(temp2[['Nome', 'Data', 'Horas_Trabalhadas',
                                    'Observacao', 'Hora_Entrada', 'Hora_Saida_Almoco',
                                    'Hora_Volta_Almoco', 'Hora_Saida', 'Hora_Nao_Identificada']])


            st.download_button(label = f'Download da Tabela de {meses[mes]}',
                               data = horas_funcionario.to_csv(index = False,na_rep = 'Nao houve'),
                               file_name = f'Horas_{func}.csv')

            horas_trabalhadas = verifica_horas_trabalhadas(horas_funcionario)

            temp4 = horas_trabalhadas[0]

            col3.markdown('\n')
            col3.markdown('\n')
            col3.markdown('\n')
            col3.markdown('\n')
            col3.markdown('\n')
            col3.subheader(f'Em {meses[mes]} de {ano}, {func} trabalhou:')
            col3.subheader(temp4)

        except:

            st.subheader(f'Não há dados, nessa data, para {func}')

    else:

        st.write('Escolha o nome do Funcionário, o Ano e o Mês desejado!')

else:
    st.write('Insira seu arquivo!')
