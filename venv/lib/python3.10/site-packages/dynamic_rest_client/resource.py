from __future__ import absolute_import
import inflection
from .query import DRESTQuery
from .record import DRESTRecord


class DRESTResource(object):

    """Represents a single resource in a DREST API.

    Arguments:
        client: a DRESTClient
        name: a resource's name
    """
    def __init__(self, client, name):
        self.name = inflection.underscore(name)
        self._client = client

    def __repr__(self):
        return self.name

    def __call__(self, **kwargs):
        return DRESTRecord(resource=self, **kwargs)

    def request(self, method, id=None, params=None, data=None):
        """Perform a request against this resource.

        Arguments:
            method: HTTP method (get, put, post, delete, options)
            id: resource ID. by default, assume no ID
            params: HTTP params
            data: HTTP data
        """
        name = self.name
        mocks = self._client.mocks.get(name)
        if method.lower() == 'get' and mocks:
            return {name: mocks}

        return self._client.request(
            method,
            self._get_url(id),
            params=params,
            data=data
        )

    def load(self, data, depth=0):
        """Loads data to an internal representation.

        Arguments:
            data: array or object
        Returns:
            Array of DRESTRecord or single DRESTRecord.
        """
        if isinstance(data, dict):
            meta = data.get('_meta', {})
            # get type from metadata
            name = meta.get('type')
            if not depth and not name:
                # fallback to current name if at depth 0
                name = self.name
            pk = meta.get('id', data.get('id'))
            if name and pk:
                # load from dict
                data['id'] = pk
                if name == self.name:
                    for key, value in data.items():
                        loaded = self.load(value, depth+1)
                        if value != loaded:
                            data[key] = loaded
                    return DRESTRecord(resource=self, **data)
                else:
                    resource = getattr(self._client, name)
                    return resource.load(data)
            else:
                # plain dict
                return data
        elif isinstance(data, list) and not isinstance(data, str):
            for i, value in enumerate(data):
                # load from list
                _value = self.load(value, depth)
                if value != _value:
                    data[i] = _value
            return data
        else:
            return data

    def create(self, **kwargs):
        record = self(**kwargs)
        record.save()
        return record

    def __getattr__(self, value):
        return getattr(DRESTQuery(self), value)

    def _get_url(self, id=None):
        return '%s%s' % (self.name, '/%s' % id if id else '')
