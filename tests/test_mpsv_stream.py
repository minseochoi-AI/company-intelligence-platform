from cil_integrations.providers.mpsv.jobs import stream_mpsv_vacancies, aggregate_by_cz_isco, CURATED_MPSV_FIXTURE


def test_mpsv_stream_parsing():
    vacancies = list(stream_mpsv_vacancies(source={"polozky": CURATED_MPSV_FIXTURE}))
    assert len(vacancies) == 3

    v1 = vacancies[0]
    assert v1["country_code"] == "CZ"
    assert v1["salary_currency"] == "CZK"
    assert v1["salary_min"] == 65000
    assert v1["salary_max"] == 95000
    assert v1["occupation_pivot"] == "2512"
    assert v1["city"] == "Praha"


def test_mpsv_stream_aggregation():
    vacancies = list(stream_mpsv_vacancies(source={"polozky": CURATED_MPSV_FIXTURE}))
    agg = aggregate_by_cz_isco(vacancies)

    # We have two 2512 (Software Developer, DevOps) and one 2511 (Data Analyst)
    assert "2512" in agg
    assert "2511" in agg

    agg_2512 = agg["2512"]
    assert agg_2512["vacancy_count"] == 2
    assert agg_2512["avg_salary_min"] == (65000 + 75000) / 2
    assert agg_2512["avg_salary_max"] == (95000 + 110000) / 2
    assert "Praha" in agg_2512["top_cities"]

    agg_2511 = agg["2511"]
    assert agg_2511["vacancy_count"] == 1
    assert agg_2511["avg_salary_min"] == 55000
    assert agg_2511["avg_salary_max"] == 80000
    assert "Brno" in agg_2511["top_cities"]


def test_mpsv_stream_limit():
    vacancies = list(stream_mpsv_vacancies(source={"polozky": CURATED_MPSV_FIXTURE}, limit=1))
    assert len(vacancies) == 1
