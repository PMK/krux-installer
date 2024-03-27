from unittest import TestCase
from unittest.mock import patch, mock_open
from src.utils.verifyer.sig_verifyer import SigVerifyer

MOCK_PEM = b"""-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEax27s943R8m9u/80/soZST64+JGLyckJ
XiyFGjKuWRkpLJzCGPW40sbXZcMOSvPBvCU2vs8Hkyfyhy4lSbySfA==
-----END PUBLIC KEY-----
"""

# pylint: disable=line-too-long
MOCK_SIG = b"0E\x02!\x00\xed\xfb\xb2\x99\x06\x99\x97fDQ\x0f%\xdf=\xe7^h\xd1\xb6n\x16\x9cBm\xc4\xcc\xbbb:P\xb5#\x02 f\xee\xf8\x95\xfd'sqH\x9eO\xa3x\xb6>\xdc\x83\x96\xd1\xf7\x92\xcf&W\xf4n\xc0\xd3\xc8\xfe\xd3\xfd"

# pylint: disable=line-too-long
MOCK_ZIP = b'PK\x03\x04\x14\x00\x00\x00\x08\x00Aj>Xf\x088\xde\xec\x02\x00\x00H\x07\x00\x00\t\x00\x1c\x00README.mdUT\t\x00\x03:!\xb9ex\xe3\xbbeux\x0b\x00\x01\x04\xe8\x03\x00\x00\x04\xe8\x03\x00\x00\xadT\xc1\x8e\xd30\x10\xbd\xe7+\x06\xf5B\xa5\xa6\xdeE\x0b\x87\x95*\x04\x8b\x80\xd5\xb2\x12\x12\xcb\x01UHu\x9cib\xd5\x89\x83\xed\xa4\x9b\x1b\x1f\xc8G1\xb6\x13\xb5\xddv\x11\x8b8$J\xc6\x9e\xf7\xde<\xcfx\x027\xa6\xbd\x87\xeb\xda:\xae\x14\x9a$Y>[\xbem\xa5\xca\xa1\xe2\xb2\x86\xcc\xf0Z\x94\xdf\x9f\x97\xce5\xf6\x92\xb1B\xba\xb2\xcd\xe6BW\xcc\xa2Z\x8b\xd6:\x9d\xf7lC \xa9\x1cA\x18\x17N\xea\xda\xb2\xad6\x9b\xb5\xd2[\xcb2\x0f9\xef+\xc52\x9e\x178\xb7]\xf1:b/<\xcf\xf4?2LC\rB\xe7(t\xb7\xc3\x1d\x02s\xa9YQ\xb2\x1f\xca\xe4\x0f1\x9dAd\x1b\xd9\xf5\xac0\xbc)\xf7\x94:\xbd\xc1zq\xf3\xee\xe2\xfc\xe3\x8b\xb3\xdbo_\xa6O\x80%9\x87\x16\x03\x97\x95\x05\xa7!C\xe0\xf0\xe1\xeb5d\xdcbN\x11\xadB\xd8\x172K\xd6\x8a\xdb\x12x\x9dC\x8eY[\xc0\xd2\xa3\xfc\x95M\xc4\xf8\xc6\x82tP\xeb\xed\x0c\\\x89P`\x8d\x86;"\xe1M\xa3\xa4\xe0\xde<\xc0{\x14\xad\xc3\x19l\tK\xb7\x0e\\\xdf\xc8\xba \xce>!\xdc\xcasS\x0b84\x95\xac\xb9\nH\xcb(\xcb\x7f\xae\xa5\xa9\xb6\xdc \xe8\x9aT\xfbH\x8e\x9d\x14\xb8\xd3\xb8\'l>\xe8%\x9b\xbcDV\xa0s\xc4\x95\x92\'\x86t\xb1\xc1.\n\xb1I\xa0H\t0\x1d)RO\x11"\x91b:O\x92d2\x19=M\x92[\xbeA\xb0-\x89\xe9u\x0b%\xef\x10\x9a\x9e\x8a\xaa/\x93d\xb5Z\x91\xc1e\x12\x03\x90\xa6\x1d\x1aK\xf5\xfb\x85\x93\x99\xabF\xa33\xfd\n\xc63\xcc\x07\x94_?\xf7q*hds?n\x82\x98\xe4\xf7\x11\xea\x95\xd25\x06O\x0c6\xdaJ\xa7\xe3R\x10BV\x80\x08\x1b\xd24\xce\x00\xf8\xae\x83\x13G{\xd8J\xde\xc4\xa8\xfaz$\x8dZrl\xb0\xce\xb1\x16\x12\xed\xa1\xd6 j\xd4\x18s\xc9\xb7\xcf:\x8a\x1b4\x87\x06Mw\r\xdaZ\xb4\xc1\x85\x158n7t\x13\xd4\xbc\xa0\xf8Z\x87\xa7\xe2\xe1\xecf@\xc7\x15>\x12\x87\xd6\xd9\xd0\xab4\n\xd4i46p\xa7\xc1"u8\xa9\xe4\x1d\x97\x8ag\n\x03\x9c\x9d\x81i\x0f\x0e&\x8a\xa4\xa0\x17\x14E\x92\xca\t\xbc\x0f\\\xe0G\xec\xb1\xdd\x83\x9e\x98tW\xd2ni\xc1\xca\x8a\xf8\x0c\r\xd3i\x96Lq\xb1\x819\xb3F\x9c\n\x87jF\xaf&\xf0\x89\xaa\xa4\x89Z;\x1c\xaa\x8f\xa0\x0f\x85x3\x8ed\xec\xab8H\xe8\xfd\xf6c\tC<Msi\xbda\x8b\xab\xb3\xf3\xf3\x8b\x99\x7f\xbf\x0c\xefW\xc7\xfa\xee\xe8\xf7IG\x18\xf2\x1f\xf5?,\xff\xb1\x90\xa3\xa4\xde\xa7\x90h\xc1\x1bG\x93\xb4p\x88\xa9\xedm\x1c\xb5L[\x0ck\x82\xc6W($\xa0\xa3\x12\xae\x86\xae\x19m\x0e\xcb\xfe^\xa2\xe6\xa1[\x92.yW\xfa\xab\xd1\xb3\x8d\x1dv\xfa\x14\xc6\xd5\xb4t\x95\xfa\xd7*vJ\xe9Ow@\x87\xc4\xe2g\xea\xc7\xd98\xf0\xe8\x07e\xfc\x06PK\x01\x02\x1e\x03\x14\x00\x00\x00\x08\x00Aj>Xf\x088\xde\xec\x02\x00\x00H\x07\x00\x00\t\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\xa4\x81\x00\x00\x00\x00README.mdUT\x05\x00\x03:!\xb9eux\x0b\x00\x01\x04\xe8\x03\x00\x00\x04\xe8\x03\x00\x00PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00O\x00\x00\x00/\x03\x00\x00\x00\x00'


class TestSigVerifyerDownloader(TestCase):

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_ZIP)
    def test_init(self, open_mock, mock_exists):
        sig = SigVerifyer(
            filename="test.zip", signature=MOCK_SIG, pubkey=MOCK_PEM, regexp=r".*\.zip"
        )
        sig.load()

        mock_exists.assert_called_once_with("test.zip")
        open_mock.assert_called_once_with("test.zip", "rb")

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_ZIP)
    def test_verify(self, open_mock, mock_exists):
        sig = SigVerifyer(
            filename="test.zip", signature=MOCK_SIG, pubkey=MOCK_PEM, regexp=r".*\.zip"
        )
        sig.load()

        result = sig.verify()

        mock_exists.assert_called_once_with("test.zip")
        open_mock.assert_called_once_with("test.zip", "rb")
        self.assertEqual(result, True)
