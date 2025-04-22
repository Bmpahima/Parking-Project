#פונקציה שמקבלת DF עם נתונים
#מחזירה PDF 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec

# קריאה והכנת הנתונים
df = pd.read_csv("חוברת2.csv")
df['start_time_date'] = pd.to_datetime(df['start_time'], format="%d/%m/%Y %H:%M")
df['end_time_date'] = pd.to_datetime(df['end_time'], format="%d/%m/%Y %H:%M")
df['year_month'] = df['start_time_date'].dt.to_period('M')  
df['day_in_week'] = df['start_time_date'].dt.strftime("%A")
df['time_in_minutes'] = (df['end_time_date'] - df['start_time_date']).dt.total_seconds() / 60

plt.rcParams['font.family'] = 'DejaVu Sans'

# קלט
parking_lot = input('Enter your parking lot name: ')
parking_date = input('Enter your years:')

filtered_df = df[(df[' parking_lot'] == parking_lot) & (df['year_month'] == parking_date)]

# נתונים
grouped = filtered_df.groupby('day_in_week')['time_in_minutes'].mean().reindex([
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
])
grouped_in_out = filtered_df['day_in_week'].value_counts().reindex([
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
])
all_hours = []
for _, row in filtered_df.iterrows():
    start = row['start_time_date'].replace(minute=0, second=0)
    end = row['end_time_date']
    current = start
    while current <= end:
        all_hours.append(current.hour)
        current += timedelta(hours=1)
hourly_counts = pd.Series(all_hours).value_counts().sort_index()
grouped_to_park = filtered_df.groupby('lot_number ')['time_in_minutes'].sum()

# יצירת PDF
with PdfPages('parking_report.pdf') as pdf:
    fig = plt.figure(figsize=(11.7, 15))  # עמוד אחד
    gs = gridspec.GridSpec(6, 2, height_ratios=[0.35, 0.2, 0.05, 1, 0.05, 1], hspace=0.5)

    # כותרת
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    ax_title.text(0.5, 0.6, "Monthly Statistics", fontsize=26, color='blue', ha='center')

    # שורת נתונים
    total_parkings = len(filtered_df)
    total_time = filtered_df['time_in_minutes'].sum()
    avg_duration = filtered_df['time_in_minutes'].mean()
    summary = (
        f"Parking Lot: {parking_lot}     Month: {parking_date}\n"
        f"Total parkings: {total_parkings}     "
        f"Total time: {total_time:.2f} minutes     "
        f"Average duration: {avg_duration:.2f} minutes"
    )
    ax_text = fig.add_subplot(gs[1, :])
    ax_text.axis('off')
    ax_text.text(0.5, 0.5, summary, fontsize=12, ha='center')

    # שורת רווח קטנה לפני הגרפים
    ax_spacer1 = fig.add_subplot(gs[2, :])
    ax_spacer1.axis('off')

    # גרף 1 - זמן ממוצע לפי יום
    ax1 = fig.add_subplot(gs[3, 0])
    ax1.bar(grouped.index, grouped.values)
    ax1.set_title("Avg Parking Time by Day")
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Minutes")
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y')

    # גרף 2 - מספר רכבים לפי יום
    ax2 = fig.add_subplot(gs[3, 1])
    ax2.bar(grouped_in_out.index, grouped_in_out.values)
    ax2.set_title("Number of Cars per Day")
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Cars")
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y')

    # שורת רווח קטנה בין שורות הגרפים
    ax_spacer2 = fig.add_subplot(gs[4, :])
    ax_spacer2.axis('off')

    # גרף 3 - לפי שעה
    ax3 = fig.add_subplot(gs[5, 0])
    ax3.plot(hourly_counts.index, hourly_counts.values, marker='o')
    ax3.set_title("Cars per Hour")
    ax3.set_xlabel("Hour")
    ax3.set_ylabel("Cars")
    ax3.grid(axis='y')

    # גרף 4 - לפי מספר חניה
    ax4 = fig.add_subplot(gs[5, 1])
    ax4.bar(grouped_to_park.index.astype(str), grouped_to_park.values)
    ax4.set_title("Parking Time by Spot")
    ax4.set_xlabel("Lot Number")
    ax4.set_ylabel("Minutes")
    ax4.tick_params(axis='x', rotation=90)
    ax4.grid(axis='y')

    pdf.savefig(fig)
    plt.close()

print("דו\"ח נשמר בהצלחה בשם parking_report.pdf")