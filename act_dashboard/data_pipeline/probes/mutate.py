"""N1b Gate 3 probe — write one test negative to DBD, verify, remove.

Steps:
 1. push_negatives_to_shared_lists with item {list_role: '1_word_exact',
    keyword_text: 'acttestkw12345xyz', match_type: 'EXACT'}
 2. Query shared_criterion back — confirm the test keyword exists
 3. remove_shared_criteria by resource_name — clean up
 4. Re-query to confirm it's gone

Run: python -m act_dashboard.data_pipeline.probes.mutate
"""
import json
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient
from google.protobuf.json_format import MessageToDict

from act_dashboard.data_pipeline.google_ads_mutate import (
    push_negatives_to_shared_lists, remove_shared_criteria,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
YAML_PATH = str(PROJECT_ROOT / "secrets" / "google-ads.yaml")
CLIENT_ID = 'dbd001'
DBD_CUSTOMER_ID = '5380281688'
TEST_KW = 'acttestkw12345xyz'


def main():
    client = GoogleAdsClient.load_from_storage(YAML_PATH)
    svc = client.get_service('GoogleAdsService')

    print('=' * 72)
    print(f'[1] push_negatives_to_shared_lists — add {TEST_KW!r} to 1_word_exact')
    print('=' * 72)
    push_result = push_negatives_to_shared_lists(
        client_id=CLIENT_ID,
        items=[{
            'source_table': 'search_term_reviews',
            'source_row_id': -1,  # dummy
            'keyword_text': TEST_KW,
            'match_type': 'EXACT',
            'list_role': '1_word_exact',
        }],
        google_ads_client=client,
    )
    print(json.dumps(push_result, indent=2, default=str))
    assert push_result['succeeded'], f'Expected success, got {push_result}'
    assert not push_result['failed'], f'Unexpected failure: {push_result["failed"]}'
    resource_name = push_result['succeeded'][0]['resource_name']
    criterion_id = push_result['succeeded'][0]['criterion_id']
    print(f'\n-> resource_name: {resource_name}')
    print(f'-> criterion_id:  {criterion_id}')

    print()
    print('=' * 72)
    print(f'[2] Verify via shared_criterion query')
    print('=' * 72)
    q = f"""
        SELECT shared_criterion.criterion_id,
               shared_criterion.type,
               shared_criterion.keyword.text,
               shared_criterion.keyword.match_type,
               shared_set.id, shared_set.name
        FROM shared_criterion
        WHERE shared_criterion.criterion_id = {criterion_id}
    """
    rows = list(svc.search(customer_id=DBD_CUSTOMER_ID, query=q))
    for r in rows:
        print(MessageToDict(r._pb, preserving_proto_field_name=True))
    assert rows, 'Verify query returned no rows — mutate may not have landed'

    print()
    print('=' * 72)
    print(f'[3] remove_shared_criteria — delete by resource_name')
    print('=' * 72)
    remove_result = remove_shared_criteria(
        customer_id=DBD_CUSTOMER_ID,
        resource_names=[resource_name],
        google_ads_client=client,
    )
    print(json.dumps(remove_result, indent=2, default=str))

    print()
    print('=' * 72)
    print('[4] Re-query to confirm gone')
    print('=' * 72)
    rows = list(svc.search(customer_id=DBD_CUSTOMER_ID, query=q))
    print(f'rows remaining: {len(rows)}  (expect 0)')
    assert not rows, f'Test keyword still present: {rows}'

    print('\nProbe PASSED (add + verify + remove + reverify OK)')


if __name__ == '__main__':
    main()
