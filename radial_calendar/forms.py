# forms.py
from django import forms
import csv
import io


class UploadCSVForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('This is not a csv file.')

            data_set = file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            reader = csv.reader(io_string, delimiter=',', quotechar="|")
            header = next(reader)

            if len(header) != 2:
                raise forms.ValidationError('CSV file must have exactly two columns.')

        return file
