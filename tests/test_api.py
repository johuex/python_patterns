"""
E2E (сквозные) тесты для API
"""
import requests

import config
from helpers.utils import random_sku, random_batchref, random_orderid


_baseurl = f"{config.get_api_url()}/allocate"


class TestApi:

    def test_happy_path_returns_200_and_allocated_batch(self, add_stock):
        """
        1. Создаем три партии + записываем их в БД
        2. Через API размещаем позицию на 3 шт
        ОР: позиция разместится в ранней партии
        """
        sku, othersku = random_sku(), random_sku("other")
        earlybatch = random_batchref(1)
        laterbatch = random_batchref(2)
        otherbatch = random_batchref(3)
        add_stock(
            [
                (laterbatch, sku, 100, "2011-01-02"),
                (earlybatch, sku, 100, "2011-01-01"),
                (otherbatch, othersku, 100, None),
            ]
        )
        data = {
            "orderid": random_orderid(), "sku": sku, "qty": 3}

        res = requests.post(_baseurl, json=data)

        assert res.status_code == 200
        assert res.json()["batchref"] == earlybatch

    def test_unhappy_path_returns_400_and_error_message(self):
        """
        1. Создаем товарную позицию
        2. Пробуем разместить ее в несуществующей партии (тк она не создана)
        ОР: позиция не размещена, Invalid sku
        """
        unknown_sku, orderid = random_sku(), random_orderid()
        data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}

        res = requests.post(_baseurl, json=data)

        assert res.status_code == 400
        assert res.json()["detail"] == f"Invalid sku {unknown_sku}"
