import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        if 'Country' in data.columns:
            countries = data['Country'].dropna().unique()
            countries.sort()
            return data, list(countries)
        else:
            return data, []
    except FileNotFoundError:
        st.error("파일이 존재하지 않습니다.")
        return None, []
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None, []
    
@st.cache_data
def process_multiselect_column(df, column_name):
    if column_name not in df.columns:
        st.warning(f"{column_name} 컬럼이 데이터에 없습니다.")
        return pd.Series(dtype='int64')
    
    df_processed = df.dropna(subset=[column_name])
    
    if(df_processed.empty):
        return pd.Series(dtype='int64')
    
    counts = df_processed[column_name]\
        .str.split(';').explode()\
        .value_counts()
    return counts

df_public, countries = load_data('./survey_results_small.csv')

def show_home():
    st.header("🏠 HOME")
    st.markdown("### Stack Overflow 개발자 설문조사 데이터 분석기")
    st.text("이 앱은 Streamlit을 사용하여 프로그래밍 언어 통계를 분석합니다.")
    st.text(f"로드된 원본 데이터는 총 {len(df_public):,} 명의 응답을 포함합니다.")

    st.subheader("데이터 원본 (일부)")
    st.dataframe(df_public.head())

    st.info("왼쪽 사이드바에서 메뉴를 선택하여 분석을 시작하세요.")
    
def show_language_usage(df, selected_country):
    st.header("🚀 언어 사용 현황")
    st.markdown(f"**({selected_country})** 응답자들이 가장 많이 사용한 언어입니다.")
    
    if selected_country == '전체':
        df_filtered = df
    else:
        df_filtered = df[df['Country'] == selected_country]
        
    lang_counts = process_multiselect_column(df_filtered, 'LanguageHaveWorkedWith')
    
    if lang_counts.empty:
        st.warning(f"선택된 국가({selected_country})에 대한 데이터가 없습니다.")
        return

    top_15_langs = lang_counts.head(15).reset_index()
    top_15_langs.columns = ['Language', 'Count']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Top 15 언어 (그래프)")
        fig_bar = px.bar(top_15_langs, x='Count', y='Language', orientation='h',
                         title=f"'{selected_country}'에서 가장 많이 사용된 언어 Top 15")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        st.subheader("Top 15 언어 (테이블)")
        st.dataframe(top_15_langs, use_container_width=True)
        
def show_detailed_analysis(df, selected_country):
    st.header("🔍 언어 심층 분석")
    st.markdown(f"**({selected_country})** 응답자들의 상세 언어 사용 분석입니다.")
    
    if selected_country == '전체':
        df_filtered = df
    else:
        df_filtered = df[df['Country'] == selected_country]
    
    st.subheader("분석 항목 선택하기")
    
    analysis_options = {
        "가장 많이 사용한 언어" : "LanguageHaveWorkedWith",
        "가장 배우고 싶은 언어" : "LanguageWantToWorkWith",
        "가장 많이 사용하는 데이터베이스" : "DatabaseHaveWorkedWith",
        "가장 배우고 싶은 데이터베이스" : "DatabaseWantToWorkWith",
        "가장 많이 사용한 플랫폼" : "PlatformHaveWorkedWith",
        "가장 배우고 싶은 플랫폼" : "PlatformWantToWorkWith"
    }
    
    selected_option_label = st.selectbox(
        "분석하고 싶은 주제를 선택하세요:",
        options=list(analysis_options.keys())
    )
    
    selected_column_name = analysis_options[selected_option_label]
    
    result_counts = process_multiselect_column(df_filtered, selected_column_name)
    
    if result_counts.empty:
        st.warning(f"선택된 국가({selected_country})에 대한 {selected_option_label} 데이터가 없습니다.")
        return
    
    st.subheader(f"'{selected_option_label}' 분석 결과 (Top 15)")
    
    top_15_results = result_counts.head(15).reset_index()
    top_15_results.columns = ['Item', 'Count']
    
    fig_px = px.bar(
        top_15_results,
        x="Count",
        y="Item",
        orientation='h',
        title=f"'{selected_country}'의 '{selected_option_label}' Top 15"
    )
    
    fig_px.update_layout(yaxis={'categoryorder':'total ascending'})
    
    st.plotly_chart(fig_px, use_container_width=True)
    st.dataframe(top_15_results)

if df_public is not None:
    st.sidebar.title("메뉴")
    
    selected_menu = st.sidebar.radio(
        "메뉴를 선택하세요",
        ["🏠 Home", "🚀 언어 사용 현황", "🔍 언어 심층 분석"]
    )
    
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("🌍 국가 필터")
    
    country_options = ['전체'] + countries
    
    selected_country = st.sidebar.selectbox(
        "국가를 선택하세요",
        options=country_options
    )
    
    if selected_menu == "🏠 Home":
        show_home()
    elif selected_menu == "🚀 언어 사용 현황":
        show_language_usage(df_public, selected_country)
    elif selected_menu == "🔍 언어 심층 분석":
        show_detailed_analysis(df_public, selected_country)
        
else:
    st.error("데이터 로딩에 실패하여 앱을 실행할 수 없습니다.")