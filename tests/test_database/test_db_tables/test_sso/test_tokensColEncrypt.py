from InsightUtilities import ColumnEncryption, InsightSingleton
from sqlalchemy_utils.types.encrypted.padding import InvalidPaddingError
import unittest
from tests.abstract import DatabaseTesting
from database.db_tables.sso import tb_tokens


class TestTokensColEncrypt(DatabaseTesting.DatabaseTesting):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ColumnEncryption()._set_random_key()

    def test_insert(self):
        self.db.add(tb_tokens(1, "token123"))
        self.db.commit()
        self.db.close()
        self.assertEqual("token123", self.db.query(tb_tokens).filter(tb_tokens.token_id == 1).one().refresh_token)

    def test_encrypted(self):
        self.db.add(tb_tokens(1, "token123"))
        self.db.commit()
        self.db.close()
        r = self.engine.execute("SELECT refresh_token FROM Tokens WHERE discord_user == 1").fetchone()[0]
        self.assertNotEqual(r, "token123")


class TestTokensColEncryptInvalidKey(TestTokensColEncrypt):
    def setUp(self):
        super().setUp()
        self.db.add(tb_tokens(1, "test123"))
        self.db.commit()
        self.db.close()
        ColumnEncryption()._set_random_key()

    def test_insert(self):
        self.db.add(tb_tokens(2, "test123"))
        self.db.commit()
        with self.assertRaises(InvalidPaddingError):
            self.db.query(tb_tokens).all()

    @unittest.SkipTest
    def test_encrypted(self):
        return

    def test_query(self):
        with self.assertRaises(InvalidPaddingError):
            self.db.query(tb_tokens).all()
