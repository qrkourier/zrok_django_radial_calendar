#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import matplotlib.colors as mcolors
# from adjustText import adjust_text
import os
import argparse


def is_high_contrast(color):
    """Check if a color is high contrast against white background."""
    r, g, b = mcolors.to_rgb(color)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b  # Convert to grayscale
    return gray < 0.65  # Check if the color is dark enough


# Create the parser
parser = argparse.ArgumentParser(description="Generate a plot from a CSV file.")
# Add the arguments
parser.add_argument("title", default="", help="The title of the plot.")
parser.add_argument("file_path", help="The path to the CSV file.")
parser.add_argument("--legend", default=False, help="Include a legend in the plot.", action=argparse.BooleanOptionalAction)
parser.add_argument("--labels", default=False, help="Include labels in the plot.", action=argparse.BooleanOptionalAction)
parser.add_argument("--offset", default=3, type=int, help="Offset for labels.")
parser.add_argument("--fontsize", default=8, type=int, help="Font size for labels.")
parser.add_argument("--image-type", default="svg", choices=["svg", "png"], help="The type of image to generate.")

# Parse the arguments
args = parser.parse_args()

# Now you can access the arguments as properties of `args`
title = args.title
file_path = args.file_path
legend = args.legend
labels = args.labels
offset = args.offset
fontsize = args.fontsize
# Replace with your file path
print(f"Reading data from {file_path};"
        f"generating with title '{title}',"
        f"legend '{legend}', labels '{labels}',"
        f"offset '{offset}', fontsize '{fontsize}'")
data = pd.read_csv(file_path)

# Assuming the first column contains the names and the second column contains the birthdays
label_column = data.columns[0]
date_column = data.columns[1]

data['parsed_dates'] = pd.to_datetime(data[date_column], format='%m/%d/%Y')

# Calculate the angle for month and radius for year
# data['Angle'] = 2 * pi * data['parsed_dates'].dt.month / 12
data['Angle'] = 2 * pi * ((data['parsed_dates'].dt.month - 1 + data['parsed_dates'].dt.day / 31) / 12)
max_year = data['parsed_dates'].max().year
num_decades = (max_year - data['parsed_dates'].min().year) / 10

# Adjust the radius to create a spiral effect
spiral_factor = 1 / num_decades
data['Adjusted Radius'] = (max_year - data['parsed_dates'].dt.year) + spiral_factor * data['Angle']

# Unique decades for labeling
data['Decade'] = (data['parsed_dates'].dt.year // 10) * 10
unique_decades_adjusted = sorted(data['Decade'].unique(), reverse=True)

# Filter out low contrast colors
colors = [color for color in mcolors.TABLEAU_COLORS if is_high_contrast(color)]
if len(data) > len(colors):
    css_colors = [color for color in mcolors.CSS4_COLORS.values() if is_high_contrast(color)]
    colors.extend(css_colors)

# Plotting the visualization with 1950 at the center
plt.figure(figsize=(12, 8))
ax = plt.subplot(111, polar=True)
ax.set_theta_direction(-1)
ax.set_theta_zero_location('N')

texts = []
for i, row in data.iterrows():
    ax.plot(row['Angle'], row['Adjusted Radius'], 'o', color=colors[i % len(colors)])
    if labels:
        texts.append(ax.text(row['Angle']+(offset/100), row['Adjusted Radius']+offset, f"{row[label_column]} ({row[date_column]})", color=colors[i % len(colors)], ha='left', va='top', fontsize=fontsize))

# Set up the grid and labels for months
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax.set_xticks(np.linspace(0, 2 * pi, 12, endpoint=False))
ax.set_xticklabels(months)

ax.grid(color='gray', alpha=0.2)

# Labeling each concentric ring with the decade it represents
for decade in unique_decades_adjusted:
    radius_label = max_year - decade
    if radius_label >= 0:  # Only label if the decade is within the range
        ax.text(0, radius_label, str(decade), ha='center', va='center')

# Adjust the radial ticks to match the decades
ax.set_yticks([max_year - decade for decade in unique_decades_adjusted])
ax.set_yticklabels([])
ax.invert_yaxis()

if legend:
    # Prepare legend labels
    legend_labels = [f"{row[label_column]} ({row[date_column]})" for _, row in data.iterrows()]
    plt.legend(legend_labels, loc='upper right', bbox_to_anchor=(1.3, 1.1))


# plt.tight_layout()

plt.title(title)

# Get the directory of the input CSV file
dir_path = os.path.dirname(file_path)

# Get the basename of the input CSV file
basename = os.path.splitext(os.path.basename(file_path))[0]

# Save the figure in the same directory as the CSV file, with the same basename and the .png suffix
output_path = os.path.join(dir_path, f'{basename}.{args.image_type}')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Wrote {output_path}")
