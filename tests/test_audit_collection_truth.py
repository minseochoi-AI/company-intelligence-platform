from cil_application.collection.service import CollectionService


def test_empty_collection_is_empty_and_cursor_cycle_is_error():
    class Empty:
        def fetch_page(self, parameters, cursor): return {'records': [], 'payload': {}, 'next_cursor': None}
    assert CollectionService().collect(Empty(), {}, authorized=True)['status'] == 'EMPTY'
    class Cycle:
        def fetch_page(self, parameters, cursor): return {'records': [{'id': 'x'}], 'payload': {}, 'next_cursor': 'same'}
    result = CollectionService().collect(Cycle(), {}, authorized=True, max_pages=3)
    assert result['status'] == 'ERROR' and result['error_type'] == 'PaginationCycle'
