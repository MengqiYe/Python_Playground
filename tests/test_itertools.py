# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by Mengqi.Ye on 2021/1/26
"""
from itertools import groupby
from operator import itemgetter

import numpy as np


class TestItertools:
    def setup(self):
        self.arr = np.array(
            [
                ['1', '?', '?'],
                ['0', '1', '?'],
                ['0', '0', '1'],
            ]
        )

    def test_groupby(self):
        idxes = np.where(self.arr != '?')

        print()
        print(f"idxes : {idxes}")

        for k, g in groupby(idxes, key=itemgetter(1)):
            print(k,)
            for x in g:
                print(x)