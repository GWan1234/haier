import json
import logging
from typing import List

from .attribute import HaierAttribute, V1SpecAttributeParser

_LOGGER = logging.getLogger(__name__)


class HaierDevice:
    _raw_data: dict
    _attributes: List[HaierAttribute]
    _attribute_snapshot_data: dict

    def __init__(self, client, raw: dict):
        self._client = client
        self._raw_data = raw
        self._attributes = []
        self._attribute_snapshot_data = {}

    @property
    def id(self):
        return self._raw_data['deviceId']

    @property
    def name(self):
        return self._raw_data['deviceName'] if 'deviceName' in self._raw_data else self.id

    @property
    def type(self):
        return self._raw_data['deviceType'] if 'deviceType' in self._raw_data else None

    @property
    def product_code(self):
        return self._raw_data['productCodeT'] if 'productCodeT' in self._raw_data else None

    @property
    def product_name(self):
        return self._raw_data['productNameT'] if 'productNameT' in self._raw_data else None

    @property
    def wifi_type(self):
        return self._raw_data['wifiType']

    @property
    def attributes(self) -> List[HaierAttribute]:
        return self._attributes

    @property
    def attribute_snapshot_data(self) -> dict:
        return self._attribute_snapshot_data

    async def async_init(self):
        # 解析Attribute
        # noinspection PyBroadException
        try:
            parser = V1SpecAttributeParser()
            attributes = await self._client.get_digital_model_from_cache(self)
            for item in attributes:
                try:
                    attr = parser.parse_attribute(item)
                    if attr:
                        self._attributes.append(attr)
                except:
                    _LOGGER.exception("Haier device %s attribute %s parsing error occurred", self.id, item['name'])

            iter = parser.parse_global(attributes)
            if iter:
                for item in iter:
                    self._attributes.append(item)

            snapshot_data = await self._client.get_device_snapshot_data(self.id)
            _LOGGER.debug(
                'device %s snapshot data fetch successful. data: %s',
                self.id,
                json.dumps(snapshot_data)
            )
            self._attribute_snapshot_data = snapshot_data
        except Exception:
            _LOGGER.exception('Haier device %s init failed', self.id)

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'wifi_type': self.wifi_type
        })
