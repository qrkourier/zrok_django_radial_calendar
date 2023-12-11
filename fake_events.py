import random
from datetime import datetime, timedelta


# Function to generate random dates
def random_date(start, end):
    """Return a random datetime between two datetime objects start and end"""
    return start + timedelta(
        # Get a random amount of seconds between start and end
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


# Start and end dates
start_date = datetime(1923, 1, 1)
end_date = datetime(2023, 1, 1)

# Generate 100 random dates
random_dates = [random_date(start_date, end_date).strftime("%m/%d/%Y") for _ in range(100)]

# Generate nonsensical labels
nonsensical_labels = ["Event " + str(i) for i in range(1, 1001)]

# Combine labels and dates
random_events = list(zip(nonsensical_labels, random_dates))

# Format as two-column list
formatted_list = "Label,Date\n" + "\n".join([f"{label},{date}" for label, date in random_events])

# Preview the first 10 lines of the formatted list
# print("\n".join(formatted_list.split("\n")[:10]))
print(formatted_list)
