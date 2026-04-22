"""N3 Part B regression test — Rule 5 mixed-intent downgrade.

When a search term token-matches BOTH a services-advertised phrase and a
services-not-advertised phrase, Rule 5 should return
('review', 'mixed_intent_adv_and_notadv', 'adv: ... | not-adv: ...') — not
block. Rules 2/3 (hard GAds neg-list matches) are unaffected.
"""
import duckdb
import pytest

from act_dashboard.engine.negatives.pass1 import (
    _load_client_config, classify_term,
)


@pytest.fixture
def cfg(tmp_path):
    path = str(tmp_path / 'mix.duckdb')
    con = duckdb.connect(path)
    con.execute("""CREATE TABLE act_v2_clients (
        client_id VARCHAR PRIMARY KEY, services_not_advertised VARCHAR,
        services_advertised VARCHAR, service_locations VARCHAR,
        client_brand_terms VARCHAR, rule_7_exclude_tokens VARCHAR);""")
    con.execute("""CREATE TABLE act_v2_client_settings (
        client_id VARCHAR, setting_key VARCHAR, setting_value VARCHAR);""")
    con.execute("""CREATE TABLE act_v2_negative_keyword_lists (
        list_id VARCHAR PRIMARY KEY, client_id VARCHAR, list_name VARCHAR,
        list_role VARCHAR, is_linked_to_campaign BOOLEAN);""")
    con.execute("""CREATE TABLE act_v2_negative_list_keywords (
        id BIGINT, list_id VARCHAR, client_id VARCHAR, keyword_text VARCHAR,
        match_type VARCHAR, snapshot_date DATE);""")
    con.execute("""CREATE TABLE act_v2_sticky_rejections (
        id BIGINT, client_id VARCHAR, search_term_normalized VARCHAR,
        search_term_original VARCHAR, rejected_at TIMESTAMP,
        expires_at TIMESTAMP, cycle_number INTEGER,
        reason_at_rejection VARCHAR, reason_detail_at_rejection VARCHAR,
        campaign_type_at_rejection VARCHAR, rejected_by VARCHAR,
        unrejected_at TIMESTAMP, unrejected_reason VARCHAR);""")
    con.execute("""INSERT INTO act_v2_clients VALUES
        ('mix', 'crown', 'dental implant', 'london', '', '')""")
    config = _load_client_config(con, 'mix')
    con.close()
    return config


def test_mixed_intent_downgrades_to_review(cfg):
    status, reason, detail = classify_term('dental implant with crown', cfg)
    assert (status, reason) == ('review', 'mixed_intent_adv_and_notadv'), (status, reason, detail)
    assert 'adv: dental implant' in detail
    assert 'not-adv: crown' in detail


def test_notadv_only_still_blocks(cfg):
    status, reason, detail = classify_term('dental crown only', cfg)
    assert status == 'block'
    assert reason == 'service_not_advertised'
    assert detail == 'crown'


def test_adv_only_keeps(cfg):
    status, reason, detail = classify_term('dental implant consultation', cfg)
    assert status == 'keep'
    assert reason == 'advertised_service_match'
    assert detail == 'dental implant'


def test_unrelated_query_falls_through(cfg):
    # No match at all → ambiguous (Rule 8 fallthrough, not mixed-intent)
    status, reason, _ = classify_term('random other query', cfg)
    assert reason != 'mixed_intent_adv_and_notadv'
