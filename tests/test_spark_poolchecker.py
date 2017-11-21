from poolchecker import spark_poolchecker

# UNIT TESTS
def test_url():
    assert spark_poolchecker._url('test_path') == 'https://api.ciscospark.com/v1/test_path'


def test_fix_at():
    assert spark_poolchecker.fix_at('test_token') == 'Bearer test_token'
    assert spark_poolchecker.fix_at('Bearer test_token') == 'Bearer test_token'
