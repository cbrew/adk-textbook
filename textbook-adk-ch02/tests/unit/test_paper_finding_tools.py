# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for paper finding tools."""

import pytest
from paper_finding.tools.tools import (
    search_arxiv,
    add_to_reading_list,
    get_reading_list,
    get_paper_recommendations,
    get_citation_network,
    summarize_paper
)


def test_search_arxiv():
    """Test arXiv search functionality."""
    result = search_arxiv("machine learning", max_results=5)
    
    assert "papers" in result
    assert "total_results" in result
    assert "query" in result
    assert result["query"] == "machine learning"
    assert len(result["papers"]) <= 5


def test_add_to_reading_list():
    """Test adding paper to reading list."""
    result = add_to_reading_list("user123", "2101.00001", "high")
    
    assert result["status"] == "success"
    assert "2101.00001" in result["message"]
    assert "high" in result["message"]
    assert "added_date" in result


def test_get_reading_list():
    """Test retrieving reading list."""
    result = get_reading_list("user123")
    
    assert "reading_list" in result
    assert "total_papers" in result
    assert "user_id" in result
    assert result["user_id"] == "user123"


def test_get_paper_recommendations():
    """Test paper recommendations."""
    interests = ["machine learning", "NLP"]
    result = get_paper_recommendations("user123", interests)
    
    assert "recommendations" in result
    assert "total_recommendations" in result
    assert "based_on_interests" in result
    assert result["based_on_interests"] == interests
    
    for rec in result["recommendations"]:
        assert "paper_id" in rec
        assert "title" in rec
        assert "relevance_score" in rec
        assert 0 <= rec["relevance_score"] <= 1


def test_get_citation_network():
    """Test citation network retrieval."""
    result = get_citation_network("2101.00001", depth=1)
    
    assert "paper_id" in result
    assert "references" in result
    assert "cited_by" in result
    assert "citation_count" in result
    assert "reference_count" in result
    assert result["paper_id"] == "2101.00001"


def test_summarize_paper():
    """Test paper summarization."""
    result = summarize_paper("2101.00001")
    
    assert "paper_id" in result
    assert "summary" in result
    assert "key_points" in result
    assert "methodology" in result
    assert "main_contribution" in result
    assert result["paper_id"] == "2101.00001"
    assert isinstance(result["key_points"], list)