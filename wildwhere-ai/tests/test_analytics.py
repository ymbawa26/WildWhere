from analysis.exploratory_analysis import build_exploratory_summary
from analysis.sql_analysis import load_sql_queries, run_query
from analysis.wildlife_metrics import sightings_by_park, sightings_by_species


def test_analytics_functions_run():
    assert not sightings_by_park().empty
    assert not sightings_by_species().empty
    summary = build_exploratory_summary()
    assert "outputs" in summary


def test_sql_queries_run():
    queries = load_sql_queries()
    assert len(queries) >= 10
    first_query = next(iter(queries.values()))
    assert not run_query(first_query).empty
