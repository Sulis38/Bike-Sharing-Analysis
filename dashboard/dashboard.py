import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",                      
    layout="wide"                        
)

st.title("Bike Sharing Dashboard 🚴")


df = pd.read_csv(r'dashboard\main_data.csv')

# Konversi suhu ke Celsius
df['temp_celsius_day'] = df['temp'] * 41

# Tambahkan nama musim
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
df['season_name'] = df['season'].map(season_mapping)

# Ubah kolom tanggal menjadi datetime
df['dteday'] = pd.to_datetime(df['dteday'])

# Sidebar: Filter Rentang Waktu
st.sidebar.header("Filter by Date")
start_date = st.sidebar.date_input("Start Date", value=df['dteday'].min())
end_date = st.sidebar.date_input("End Date", value=df['dteday'].max())

# Validasi rentang waktu
if start_date > end_date:
    st.sidebar.error("Tanggal awal harus lebih kecil atau sama dengan tanggal akhir.")
    st.stop()

# Filter data berdasarkan rentang waktu
filtered_data = df[(df['dteday'] >= pd.Timestamp(start_date)) & (df['dteday'] <= pd.Timestamp(end_date))]

if filtered_data.empty:
    st.warning("Tidak ada data untuk rentang waktu yang dipilih.")
    st.stop()

# Hitung metrik utama
casual_avg = filtered_data['casual'].mean()
registered_avg = filtered_data['registered'].mean()
total_user = filtered_data['cnt'].mean()

# Row 1: Metrics
col1, col2, col3= st.columns(3)
col1.metric("Average Casual Users", f"{casual_avg:.2f}")
col2.metric("Average Registered Users", f"{registered_avg:.2f}")
col3.metric("Daily Total Users ", f"{total_user:.2f}")


# Visualisasi 1: Rental Bike Over Time
st.subheader('Rental Bike Over Time')
fig, ax = plt.subplots()
ax.plot(filtered_data['dteday'], filtered_data['casual'], label='Casual', color='blue')
ax.plot(filtered_data['dteday'], filtered_data['registered'], label='Registered', color='green')
ax.tick_params(axis='x', labelsize=7)  
ax.tick_params(axis='y', labelsize=10)  
ax.set_xlabel('Date', fontsize=14)  
ax.set_ylabel('Bike Rentals', fontsize=14)  
ax.set_title('Rental Bike Over Time', fontsize=16) 
ax.legend(fontsize=10) 
st.pyplot(fig)

# Visualisasi: Rental Bike by Season dengan warna maksimum
st.subheader('Rental Bike by Season')
season_group = filtered_data.groupby('season_name')[['casual', 'registered']].sum()
season_order = ["Spring", "Summer", "Fall", "Winter"]
season_group = season_group.reindex(season_order)

max_casual = season_group['casual'].max()
max_casual_season = season_group['casual'].idxmax()

max_registered = season_group['registered'].max()
max_registered_season = season_group['registered'].idxmax()

casual_colors = [
    'red' if season == max_casual_season else 'lightblue'
    for season in season_group.index
]

registered_colors = [
    'green' if season == max_registered_season else 'lightgray'
    for season in season_group.index
]

# Plot bar chart
fig, ax = plt.subplots(figsize=(10, 6))
bar_width = 0.4 
x_positions = range(len(season_group.index))
ax.bar(
    [x - bar_width / 2 for x in x_positions],
    season_group['casual'],
    width=bar_width,
    color=casual_colors,
    edgecolor='black',
    label='Casual'
)

ax.bar(
    [x + bar_width / 2 for x in x_positions],
    season_group['registered'],
    width=bar_width,
    color=registered_colors,
    edgecolor='black',
    label='Registered'
)

ax.set_xticks(x_positions)
ax.set_xticklabels(season_group.index)
ax.set_xlabel('Season')
ax.set_ylabel('Total Rentals')
ax.set_title('Rental Bike by Season')
ax.legend()

st.pyplot(fig)


# Visualisasi: Penyewaan sepeda berdasarkan kategori suhu dengan bar plot horizontal
st.subheader('Rental Bike by Temperature')
st.markdown('### Category Temp (°C)')
filtered_data['temp_category'] = pd.cut(
    filtered_data['temp_celsius_day'],
    bins=[-5, 10, 20, 30, 40],
    labels=['Cold', 'Cool', 'Warm', 'Hot']
)

temp_counts = filtered_data.groupby('temp_category')['cnt'].mean()
max_value = temp_counts.max()
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['red' if value == max_value else 'blue' for value in temp_counts]  # Warna merah untuk nilai maksimum

temp_counts.plot(kind='barh', ax=ax, color=colors)

fig, ax = plt.subplots(figsize=(8, 5))
temp_counts.plot(kind='barh', ax=ax, color=['orange', 'orange', 'red', 'orange'])

for index, value in enumerate(temp_counts):
    ax.text(value, index, f'{value:.0f}', va='center', fontsize=10, color='black', fontweight='bold')

ax.set_xlabel('Total Rentals')
ax.set_ylabel('Temperature Category')
ax.set_title('Rental Bike by Temperature Category')
st.pyplot(fig)

# Row 3: Rental Bike in Different Situations
st.subheader('Correlation Enviroment Situations to Rental Bike')
col1, col2 = st.columns(2)

# Kolom 1: Kategori Suhu
with col1:
    st.markdown('### Temp vs Rentals')
    fig, ax = plt.subplots()
    ax.scatter(filtered_data['temp_celsius_day'], filtered_data['cnt'], alpha=0.5, color='orange')
    
    # Menambahkan garis tren
    slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_data['temp_celsius_day'], filtered_data['cnt'])
    ax.plot(filtered_data['temp_celsius_day'], slope * filtered_data['temp_celsius_day'] + intercept, color='red', linewidth=2)

    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Total Rentals')
    st.pyplot(fig)

# Kolom 2: Scatter Plot Temp vs Rentals
with col2:
    st.markdown('### Correlation Matrix')
    env_factors = ['temp_celsius_day', 'casual', 'hum', 'weathersit', 'windspeed']
    corr = filtered_data[env_factors].corr()
    fig, ax = plt.subplots(figsize=(5, 4))  # Ukuran disesuaikan
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
