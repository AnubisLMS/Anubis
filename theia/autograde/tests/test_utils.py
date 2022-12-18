import os
import random
import string

import flask
import pytest

from anubis_autograde.utils import (
    expand_path,
    remove_unprintable,
    text_response,
    colorize_render,
)


class TestUtils:
    def test_expand_path(self, pytester):
        pytester.mkdir('test')
        test_txt = pytester.path.joinpath('test/test.txt')
        test_txt.write_text('abc123')
        assert os.listdir('test') == ['test.txt']
        assert expand_path('*/*.txt') == 'test/test.txt'

    @pytest.fixture()
    def printable(self) -> str:
        return string.printable

    @pytest.fixture()
    def unprintable(self, printable) -> str:
        return ''.join(chr(c) for c in range(0, 256) if chr(c) not in printable)

    def test_remove_unprintable_str(self, unprintable):
        for _ in range(10):
            c = random.choice(unprintable)
            assert remove_unprintable(f'{c}abc{c}123{c}') == 'abc123'

    def test_remove_unprintable_bytes(self, unprintable):
        for _ in range(10):
            c = random.choice(unprintable)
            assert remove_unprintable(f'{c}abc{c}123{c}'.encode()) == 'abc123'

    def test_text_response_text(self, app):
        @text_response
        def view1():
            return 'abc123'
        with app.app_context():
            r = view1()
        assert type(r) == flask.Response
        assert r.status_code == 200
        assert r.content_type == 'text/plain'
        assert r.data == b'abc123\n'

    def test_text_response_text_status(self, app):
        @text_response
        def view1():
            return 'abc123', 400

        with app.app_context():
            r = view1()
        assert type(r) == flask.Response
        assert r.status_code == 400
        assert r.content_type == 'text/plain'
        assert r.data == b'abc123\n'

    def test_colorize_render(self):
        assert colorize_render('test') == '\x1b[36mtest\x1b[0m'
        assert colorize_render('test', termcolor_args=('red',)) == '\x1b[31mtest\x1b[0m'
