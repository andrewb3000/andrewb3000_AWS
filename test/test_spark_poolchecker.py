# UNIT TESTS
def test_url():
    assert _url('test_path') == 'https://api.ciscospark.com/v1/test_path'


def test_fix_at():
    assert fix_at('test_token') == 'Bearer test_token'
    assert fix_at('Bearer test_token') == 'Bearer test_token'
