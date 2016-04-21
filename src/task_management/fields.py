from django import forms


class MultiFileInput(forms.FileInput):
    """ Multi file field widget """
    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class MultiFileField(forms.FileField):
    """ Multiple file field """
    widget = MultiFileInput

    def to_python(self, data):
        result = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                result.append(i)

        return result
