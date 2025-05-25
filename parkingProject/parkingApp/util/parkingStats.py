import os
import sys
import django
sys.path.append('/Users/bmpahima/Desktop/final-project/Parking-Project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
from django.core.mail import EmailMessage
from django.conf import settings
django.setup()

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
from parkingAuth.models import ParkingHistory, parkingAuth
from parkingApp.models import ParkingLot
from io import BytesIO


def get_parking_lot_stat(id, parking_lot_id=8, month=3, year=2025):
    """
    Generates and emails a statistical parking report (PDF) for a given parking lot,
    based on parking history data, for a specific month or year.

    The report includes:
    - Average parking time per day of week
    - Number of parked vehicles per day
    - Vehicles per hour distribution
    - Total parking time per parking spot
    - Summary statistics including utilization rate

    Args:
        id (int): The ID of the parking lot owner (used to fetch email address).
        parking_lot_id (int): ID of the ParkingLot model instance.
        month (int): The month to generate the report for (0 means yearly report).
        year (int): The year of the report.

    Returns:
        str or None: Returns "success" if the report was generated and sent successfully,
                     otherwise returns None in case of errors or missing data.

    Side Effects:
        - Creates a PDF file in memory.
        - Sends an email with the PDF attachment to the parking lot owner.
    """
    
    if not ParkingHistory.objects.filter(parking__parking_lot__id=parking_lot_id).exists():
        return None
    qs = ParkingHistory.objects.filter(parking__parking_lot__id=parking_lot_id).values()
    df = pd.DataFrame(list(qs))

    df.dropna(inplace=True)
    df['day_in_week'] = df['start_time'].dt.strftime("%A")
    df['time_in_minutes'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    plt.rcParams['font.family'] = 'DejaVu Sans'

    if not ParkingLot.objects.filter(id=parking_lot_id).exists():
        return None
    selected_parking_lot = ParkingLot.objects.get(id=parking_lot_id)
    parking_lot = selected_parking_lot.name
    pdf_title = ""

    if month != 0:
        filtered_df = df[(df['start_time'].dt.month == month)]
        pdf_title = "ParkVision - Monthly Statistics"
    else:
        filtered_df = df[(df['start_time'].dt.year == year)]
        pdf_title = "ParkVision - Yearly Statistics"

    total_cars_parked = filtered_df.shape[0]

    #Data
    grouped = filtered_df.groupby('day_in_week')['time_in_minutes'].mean().reindex([
        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
    ]).fillna(0)
   
    grouped_in_out = filtered_df['day_in_week'].value_counts().reindex([
        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
    ]).fillna(0)
         
    hourly_counts = filtered_df['start_time'].dt.hour.value_counts().sort_index()

    grouped_to_park = filtered_df.groupby('parking_id')['time_in_minutes'].sum()

    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig = plt.figure(figsize=(11.7, 15)) 
        gs = gridspec.GridSpec(6, 2, height_ratios=[0.35, 0.2, 0.05, 1, 0.05, 1], hspace=0.5)

        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.8, pdf_title, fontsize=36, color='#0234b3', ha='center', weight='bold')
        total_parking_spots = selected_parking_lot.parking_spots
        total_time = filtered_df['time_in_minutes'].sum()
        avg_duration = filtered_df['time_in_minutes'].mean()
        total_time_in_hours = total_time / 60 #minutes for hours
        total_hours_in_month = 30 * 24
        utilization_rate = (total_time_in_hours / (total_parking_spots * total_hours_in_month)) * 100
        summary1 = (
            f"Parking Lot Name:\n"
            f"Reported Date:\n"
            f"Total Parking Spaces:\n"
            f"Total Vehicles Parked:\n"
            f"Total Parking Time (m):\n"
            f"Average Parking Time (m):\n"
            f"Parking Utilization Rate: "
        )
        summary = (
            f"{parking_lot}\n"
            f"{f'{year}-{month:02d}' if month != 0 else f'{year}'}\n"
            f"{total_parking_spots}\n"
            f"{total_cars_parked}\n"
            f"{total_time:.2f}\n"
            f"{avg_duration:.2f}\n"
            f"{utilization_rate:.2f}%"
        )

        ax_text1 = fig.add_subplot(gs[1, 0])
        ax_text1.axis('off')
        ax_text1.text(0.4, 0.0, summary1, fontsize=16, ha='left', weight='bold')

        ax_text = fig.add_subplot(gs[1, 1])
        ax_text.axis('off')
        ax_text.text(0.6, 0.0, summary, fontsize=16, ha='right')

        ax_spacer1 = fig.add_subplot(gs[2, :])
        ax_spacer1.axis('off')

        #Graph 1 - average time based on day
        ax1 = fig.add_subplot(gs[3, 0])
        ax1.bar(grouped.index, grouped.values, color="#0253ff")
        ax1.set_title("Average Parking Time per Day")
        ax1.set_xlabel("Day")
        ax1.set_ylabel("Minutes")
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y')

        #Graph 2 - number of vehicles for a day
        ax2 = fig.add_subplot(gs[3, 1])
        ax2.bar(grouped_in_out.index, grouped_in_out.values, color="#0253ff")
        ax2.set_title("Number of Cars per Day")
        ax2.set_xlabel("Day")
        ax2.set_ylabel("Cars")
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y')

        ax_spacer2 = fig.add_subplot(gs[4, :])
        ax_spacer2.axis('off')

        #Graph 3 - by Hour
        ax3 = fig.add_subplot(gs[5, 0])
        ax3.plot(hourly_counts.index, hourly_counts.values, marker='o', color="#0253ff")
        ax3.set_title("Vehicles per Hour")
        ax3.set_xlabel("Hour")
        ax3.set_ylabel("Cars")
        ax3.grid(axis='y')

        #Graph 4 - By parking number
        ax4 = fig.add_subplot(gs[5, 1])
        ax4.bar(grouped_to_park.index.astype(str), grouped_to_park.values, color="#0253ff")
        ax4.set_title("Parking Time per Spot")
        ax4.set_xlabel("Parking Spot Number")
        ax4.set_ylabel("Minutes")
        ax4.tick_params(axis='x', rotation=90)
        ax4.grid(axis='y')

        pdf.savefig(fig)
        plt.close()

    buffer.seek(0)
    
    owner = parkingAuth.objects.get(id=id)
    if owner:
        email = EmailMessage(
            subject="Parking Report",
            body="Please find the attached parking report.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[owner.email],
        )
        email.attach("parking_report.pdf", buffer.read(), "application/pdf")
        email.send()
        buffer.close()
    else:
        return None

    return "success"

if __name__ == "__main__":
    value = get_parking_lot_stat(15)
    print(value)