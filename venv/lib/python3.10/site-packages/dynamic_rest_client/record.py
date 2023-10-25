from __future__ import absolute_import
from .utils import unpack
from .exceptions import DoesNotExist
import copy
from six import string_types


class DRESTRecord(object):

    def __init__(self, resource, **data):
        self._resource = resource
        self._load(data)

    def delete(self):
        id = self.id
        self._resource.request(
            'delete',
            id=id,
        )
        self.id = None

    def save(self):
        id = self.id
        new = not id
        data = (
            self._get_data() if new
            else self._serialize(self._get_diff())
        )
        if data:
            if new:
                data.pop('id', None)
            response = self._resource.request(
                'post' if new else 'patch',
                id=id,
                data=data
            )
            self._load(unpack(response))

    def reload(self):
        id = self.id
        if id:
            response = self._resource.request('get', id=id)
            self._load(unpack(response))
        else:
            raise DoesNotExist()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    @property
    def dict(self):
        return self._get_data()

    def __eq__(self, other):
        if hasattr(other, '_get_data'):
            other = other._get_data()
        return self._get_data() == other

    def __repr__(self):
        return '%s.%s' % (self._resource.name, self.id if self.id else '')

    def _get_data(self, fn=None):
        if fn is None:
            flt = lambda k, v: not k.startswith('_')
        else:
            flt = lambda k, v: fn(k, v)

        return {
            k: v for k, v in self.__dict__.items()
            if flt(k, v)
        }

    def _get_diff(self):
        return self._get_data(
            lambda k, v: (
                not k.startswith('_') and
                (k not in self._clean or v != self._clean[k])
            )
        )

    def __deepcopy__(self, memo):
        data = self.__dict__
        new_data = self._get_data()
        for key, value in memo.items():
            new_value = data.get(key)
            if isinstance(new_value, dict):
                if value != new_value:
                    new_value = copy.copy(new_value)
                    new_value.update(value)
            elif (
                isinstance(new_value, (list, tuple)) and
                not isinstance(new_value, string_types)
            ):
                if value != new_value:
                    new_value = list(set(new_value + list(value)))
            new_data[key] = new_value
        return new_data

    def _load(self, data):
        for key, value in data.items():
            setattr(self, key, value)

        self._clean = copy.deepcopy(self)
        self.id = data.get('_meta', {}).get('id', data.get('id', None))

    def _serialize(self, data):
        for key, values in data.items():
            if isinstance(values, list):
                if len(values) > 0:
                    for i, value in enumerate(values):
                        if isinstance(value, DRESTRecord):
                            values[i] = value.id
            elif isinstance(values, DRESTRecord):
                data[key] = values.id
        return data
