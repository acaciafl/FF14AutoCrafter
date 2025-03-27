import pytest
import traceback
import ff14_auto_crafter as ac


def test_read_tsv_file():
    operations = None
    try:
        operations = ac.read_tsv_file('operation_sample.tsv')

        result = True
    except Exception as e:
        result = False
        print(traceback.format_exc())

    assert result == True

    print("operations: " + str(operations))
