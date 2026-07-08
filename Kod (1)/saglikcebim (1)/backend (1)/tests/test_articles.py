from app.api.v1 import articles as articles_api


def test_daily_articles_success(client, auth_headers, monkeypatch):
    async def fake_search_pubmed_by_query(**_kwargs):
        return [
            {
                "pmid": "12345",
                "title": "LDL Cholesterol and cardiovascular risk",
                "authors": "Doe et al.",
                "journal": "Med J",
                "pub_date": "2025",
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345/",
                "abstract": "Elevated LDL was associated with higher risk. Lifestyle reduced risk.",
            }
        ]

    monkeypatch.setattr(articles_api, "search_pubmed_by_query", fake_search_pubmed_by_query)

    res = client.get("/articles/daily?limit=5", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert "articles" in body
    assert len(body["articles"]) == 1
    assert body["articles"][0]["pmid"] == "12345"


def test_search_articles_success(client, auth_headers, monkeypatch):
    async def fake_search_pubmed_by_query(**_kwargs):
        return [
            {
                "pmid": "222",
                "title": "Triglyceride and diet changes",
                "authors": "Smith et al.",
                "journal": "Cardio Updates",
                "pub_date": "2026",
                "url": "https://pubmed.ncbi.nlm.nih.gov/222/",
                "abstract": "Diet intervention reduced cholesterol and lipid levels significantly in adults.",
            },
            {
                "pmid": "333",
                "title": "Exercise and lipid profile",
                "authors": "Lee et al.",
                "journal": "Preventive Health",
                "pub_date": "2026",
                "url": "https://pubmed.ncbi.nlm.nih.gov/333/",
                "abstract": "Regular exercise improved HDL cholesterol and reduced cardiovascular lipid risk.",
            },
        ]

    monkeypatch.setattr(articles_api, "search_pubmed_by_query", fake_search_pubmed_by_query)

    res = client.post(
        "/articles/search",
        json={
            "query": "cholesterol management",
            "max_results": 6,
            "include_focus": True,
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["articles"]
    assert body["summary"]


def test_articles_chat_with_context_articles(client, auth_headers):
    res = client.post(
        "/articles/chat",
        json={
            "message": "Kolesterolu dusurmek icin bu calismalar ne diyor?",
            "focus_tests": ["kolesterol", "trigliserid"],
            "articles": [
                {
                    "pmid": "555",
                    "title": "Lifestyle and cholesterol reduction",
                    "abstract": "Mediterranean diet was associated with lower LDL cholesterol.",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/555/",
                },
                {
                    "pmid": "556",
                    "title": "Physical activity for lipids",
                    "abstract": "Higher activity improved HDL and reduced triglycerides.",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/556/",
                },
            ],
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["answer"]
    assert len(body["references"]) >= 1
