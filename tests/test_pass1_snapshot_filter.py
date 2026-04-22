"""N2 Part 1 regression test: Pass 1 must only read the latest neg-list
snapshot, not the union across every historical snapshot.

Seeds a minimal in-memory-ish DuckDB with two snapshots for one client:
  - 2026-04-20: ['badword', 'oldword']   (linked, EXACT 1-word list)
  - 2026-04-21: ['badword']               (oldword removed)

Expected:
  - classify_term('oldword', cfg) -> NOT blocked (oldword no longer in latest)
  - classify_term('badword', cfg) -> blocked
"""
import os
import tempfile
from datetime import date

import duckdb
import pytest

from act_dashboard.engine.negatives.pass1 import (
    _load_client_config, classify_term,
)


@pytest.fixture
def db_with_two_snapshots(tmp_path):
    path = str(tmp_path / 'snap.duckdb')
    con = duckdb.connect(path)
    # Minimal client table (Pass 1 only reads the 5 config cols)
    con.execute("""
        CREATE TABLE act_v2_clients (
            client_id VARCHAR PRIMARY KEY,
            services_not_advertised VARCHAR,
            services_advertised VARCHAR,
            service_locations VARCHAR,
            client_brand_terms VARCHAR,
            rule_7_exclude_tokens VARCHAR
        );
    """)
    con.execute("""
        CREATE TABLE act_v2_client_settings (
            client_id VARCHAR,
            setting_key VARCHAR,
            setting_value VARCHAR
        );
    """)
    con.execute("""
        CREATE TABLE act_v2_negative_keyword_lists (
            list_id VARCHAR PRIMARY KEY,
            client_id VARCHAR,
            list_name VARCHAR,
            list_role VARCHAR,
            is_linked_to_campaign BOOLEAN
        );
    """)
    con.execute("""
        CREATE TABLE act_v2_negative_list_keywords (
            id BIGINT,
            list_id VARCHAR,
            client_id VARCHAR,
            keyword_text VARCHAR,
            match_type VARCHAR,
            snapshot_date DATE
        );
    """)
    con.execute("""
        CREATE TABLE act_v2_sticky_rejections (
            id BIGINT, client_id VARCHAR, search_term_normalized VARCHAR,
            search_term_original VARCHAR, rejected_at TIMESTAMP,
            expires_at TIMESTAMP, cycle_number INTEGER,
            reason_at_rejection VARCHAR, reason_detail_at_rejection VARCHAR,
            campaign_type_at_rejection VARCHAR, rejected_by VARCHAR,
            unrejected_at TIMESTAMP, unrejected_reason VARCHAR
        );
    """)
    con.execute("""INSERT INTO act_v2_clients VALUES
        ('testclient','','dental implants','london','','')""")
    con.execute("""INSERT INTO act_v2_negative_keyword_lists VALUES
        ('testclient-gal-1','testclient','1 WRD [ex]','1_word_exact',TRUE)""")
    # Snapshot 20/4: badword + oldword
    con.execute("""INSERT INTO act_v2_negative_list_keywords VALUES
        (1,'testclient-gal-1','testclient','badword','EXACT','2026-04-20'),
        (2,'testclient-gal-1','testclient','oldword','EXACT','2026-04-20')""")
    # Snapshot 21/4: badword only (oldword removed)
    con.execute("""INSERT INTO act_v2_negative_list_keywords VALUES
        (3,'testclient-gal-1','testclient','badword','EXACT','2026-04-21')""")
    con.close()
    yield path


def test_pass1_reads_only_latest_snapshot(db_with_two_snapshots):
    con = duckdb.connect(db_with_two_snapshots)
    try:
        cfg = _load_client_config(con, 'testclient')
    finally:
        con.close()

    assert cfg is not None
    # Snapshot date surfaced in cfg
    assert str(cfg['neg_snapshot_date']) == '2026-04-21'

    # badword still present in latest → Rule 2 blocks
    status, reason, _ = classify_term('badword', cfg)
    assert status == 'block'
    assert reason == 'existing_exact_neg_match'

    # oldword was removed in latest → must NOT be classified as Rule 2 block
    status2, reason2, _ = classify_term('oldword', cfg)
    assert not (status2 == 'block' and reason2 == 'existing_exact_neg_match'), (
        "Pass 1 still sees 'oldword' as an exact neg even though it was "
        "removed in the 2026-04-21 snapshot — snapshot_date filter regressed."
    )


def test_pass1_empty_when_no_snapshot(tmp_path):
    path = str(tmp_path / 'empty.duckdb')
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
        ('nosnap','','dental implants','london','','')""")
    cfg = _load_client_config(con, 'nosnap')
    con.close()

    assert cfg is not None
    assert cfg['neg_snapshot_date'] is None
    assert cfg['exact_neg_phrases'] == {}
    assert cfg['phrase_neg_phrases'] == {}
    assert cfg['exact_neg_single_words'] == set()
