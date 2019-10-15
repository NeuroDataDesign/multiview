import sys
import pytest
from multiview.embed.base import BaseEmbed
from numpy.testing import assert_equal


def test_base_embed():
    base = BaseEmbed()

    assert_equal(base._pairwise())
    base.fit(Xs=None, y=None)
    base.transform(Xs=None)
    base.fit_transform(Xs=None, y=None)
